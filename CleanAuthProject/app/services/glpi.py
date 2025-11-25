import requests
import logging
from typing import Any, Dict
from config import settings
from .http_client import build_session

_session: requests.Session | None = None
_api_base: str | None = None

def get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = build_session(settings.request_timeout, verify=settings.verify_ssl)
    return _session

def _get_api_base() -> str:
    global _api_base
    if _api_base is None:
        base = settings.glpi_url.rstrip("/")
        if base.endswith("/apirest.php"):
            _api_base = base
        else:
            _api_base = f"{base}/apirest.php"
    return _api_base

def _headers(session_token: str | None = None) -> Dict[str, str]:
    h = {"App-Token": settings.glpi_app_token, "Content-Type": "application/json"}
    if session_token:
        h["Session-Token"] = session_token
    return h

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    settings.validate()
    s = get_session()
    resolved = search_user_by_email(email) or {}
    login = resolved.get("login") or email
    url = f"{_get_api_base()}/initSession"
    payload = {"login": login, "password": password}
    try:
        r = s.post(url, json=payload, headers=_headers(), timeout=getattr(s, "request_timeout", 10))
    except requests.exceptions.RequestException as e:
        raise RuntimeError("glpi_unavailable") from e
    if r.status_code == 401:
        raise PermissionError("invalid_credentials")
    if r.status_code >= 500:
        raise RuntimeError("glpi_unavailable")
    r.raise_for_status()
    j = r.json()
    session_token = j.get("session_token") or j.get("session", {}).get("token") or j.get("session")
    user_info = j.get("user") or {}
    user_id = user_info.get("id") or user_info.get("users_id")
    login_out = user_info.get("name") or user_info.get("login") or login
    email_out = user_info.get("email") or email
    if not user_id or not session_token:
        url_full = f"{_get_api_base()}/getFullSession"
        rf = s.get(url_full, headers=_headers(session_token))
        if rf.ok:
            jf = rf.json()
            user_full = jf.get("user") or {}
            user_id = user_id or user_full.get("id") or user_full.get("users_id")
            login_out = login_out or user_full.get("name") or user_full.get("login")
            email_out = email_out or user_full.get("email")
    return {"session_token": session_token, "user_id": user_id, "login": login_out, "email": email_out}

def authenticate_with_user_token(user_token: str) -> Dict[str, Any]:
    settings.validate()
    s = get_session()
    url = f"{_get_api_base()}/initSession"
    payload = {"user_token": user_token}
    try:
        r = s.post(url, json=payload, headers=_headers(), timeout=getattr(s, "request_timeout", 10))
    except requests.exceptions.RequestException as e:
        raise RuntimeError("glpi_unavailable") from e
    if r.status_code == 401:
        raise PermissionError("invalid_credentials")
    if r.status_code >= 500:
        raise RuntimeError("glpi_unavailable")
    r.raise_for_status()
    j = r.json()
    session_token = j.get("session_token") or j.get("session", {}).get("token") or j.get("session")
    user_info = j.get("user") or {}
    return {"session_token": session_token, "user_id": user_info.get("id") or user_info.get("users_id"), "login": user_info.get("name") or user_info.get("login"), "email": user_info.get("email")}

def create_ticket(session_token: str, title: str, description: str, category_id: int, requesttype_id: int | None = None, type_: int = 1, status: int = 2) -> Dict[str, Any]:
    s = get_session()
    uid = _get_user_id_from_session(session_token)
    if not uid:
        raise PermissionError("invalid_session")
    input_data: Dict[str, Any] = {"name": title, "content": description, "itilcategories_id": category_id, "type": type_, "status": status, "_users_id_requester": uid, "users_id_recipient": uid}
    if isinstance(requesttype_id, int) and requesttype_id > 0:
        input_data["requesttypes_id"] = requesttype_id
    payload = {"input": input_data}
    url = f"{_get_api_base()}/Ticket"
    r = s.post(url, json=payload, headers=_headers(session_token))
    ok = r.ok
    ct = r.headers.get("content-type", "")
    resp_json = r.json() if ct.startswith("application/json") else {}
    tid = None
    if isinstance(resp_json, dict):
        tid = resp_json.get("id") or resp_json.get("tickets_id") or resp_json.get("ticket_id")
    elif isinstance(resp_json, list) and resp_json:
        first = resp_json[0]
        if isinstance(first, dict):
            tid = first.get("id") or first.get("tickets_id")
    return {"ok": ok, "id": tid, "name": title, "status": status, "json": (resp_json if resp_json else r.text)}

def _status_name(code: int) -> str:
    return {1: "Novo", 2: "Em andamento", 3: "Planejado", 4: "Pendente", 5: "Resolvido", 6: "Fechado"}.get(code, str(code))

def _get_user_id_from_session(session_token: str) -> int | None:
    s = get_session()
    r = s.get(f"{_get_api_base()}/getFullSession", headers=_headers(session_token))
    if not r.ok:
        return None
    j = r.json()
    sess = j.get("session") or {}
    return sess.get("glpiID") or sess.get("id")

def _get_assignee_name(session_token: str, ticket_id: int) -> str | None:
    s = get_session()
    r = s.get(f"{_get_api_base()}/Ticket/{ticket_id}/Ticket_User", headers=_headers(session_token))
    if not r.ok:
        return None
    arr = r.json()
    assignee_id = None
    for it in arr:
        if it.get("type") == 2:
            assignee_id = it.get("users_id")
            break
    if not assignee_id:
        return None
    ru = s.get(f"{_get_api_base()}/User/{assignee_id}", headers=_headers(session_token))
    if not ru.ok:
        return None
    uj = ru.json()
    return uj.get("name") or uj.get("realname")

def list_user_tickets(session_token: str, unresolved: bool = True, page: int = 1, page_size: int = 10, sort: str = "updated_desc") -> Dict[str, Any]:
    user_id = _get_user_id_from_session(session_token)
    if not user_id:
        raise PermissionError("invalid_session")
    s = get_session()
    logging.info(f"[list_user_tickets] user_id={user_id} unresolved={unresolved} page={page} page_size={page_size} sort={sort}")
    params: Dict[str, Any] = {}
    params["forcedisplay[0]"] = "2"
    params["forcedisplay[1]"] = "1"
    params["forcedisplay[2]"] = "12"
    params["forcedisplay[3]"] = "15"
    params["forcedisplay[4]"] = "16"
    if unresolved:
        params["criteria[0][field]"] = "12"
        params["criteria[0][searchtype]"] = "notequals"
        params["criteria[0][value]"] = "5"
        params["criteria[1][link]"] = "AND"
        params["criteria[1][field]"] = "12"
        params["criteria[1][searchtype]"] = "notequals"
        params["criteria[1][value]"] = "6"
    params["range"] = "0-199"
    if sort == "updated_desc":
        params["sort"] = "16"
        params["order"] = "DESC"
    elif sort == "updated_asc":
        params["sort"] = "16"
        params["order"] = "ASC"
    elif sort == "created_desc":
        params["sort"] = "15"
        params["order"] = "DESC"
    elif sort == "created_asc":
        params["sort"] = "15"
        params["order"] = "ASC"
    url = f"{_get_api_base()}/Ticket"
    req_params = {"range": "0-499"}
    arr_all: list[Dict[str, Any]] = []
    ranges = [(0, 499), (500, 999), (1000, 1499), (1500, 1999)]
    sort_field = None
    sort_order = None
    if sort == "updated_desc":
        sort_field, sort_order = "date_mod", "DESC"
    elif sort == "updated_asc":
        sort_field, sort_order = "date_mod", "ASC"
    elif sort == "created_desc":
        sort_field, sort_order = "date", "DESC"
    elif sort == "created_asc":
        sort_field, sort_order = "date", "ASC"
    for start, end in ranges:
        batch_params = {"range": f"{start}-{end}"}
        if sort_field and sort_order:
            batch_params["sort"] = sort_field
            batch_params["order"] = sort_order
        rb = s.get(url, params=batch_params, headers=_headers(session_token))
        if not rb.ok:
            try:
                ct = rb.headers.get("content-type", "")
                body = rb.text if not ct.startswith("application/json") else rb.json()
                logging.info(f"[list_user_tickets] glpi_ticket_error status={rb.status_code} body={body}")
            except Exception:
                logging.info(f"[list_user_tickets] glpi_ticket_error status={rb.status_code} body=<unavailable>")
            continue
        jd = rb.json()
        batch = jd if isinstance(jd, list) else []
        arr_all.extend(batch)
        logging.info(f"[list_user_tickets] glpi_endpoint=/Ticket params={batch_params} raw_count={len(batch)}")
        if len(batch) < (end - start + 1):
            break
    arr = arr_all
    for t in arr[:5]:
        logging.info(f"[list_user_tickets] raw_item id={t.get('id')} name={t.get('name')} status={t.get('status')}")
    items: list[Dict[str, Any]] = []
    requester_count = 0
    seen_ids: set[int] = set()
    for t in arr:
        tid = t.get("id")
        if not tid or tid in seen_ids:
            continue
        seen_ids.add(int(tid))
        recipient = t.get("users_id_recipient")
        status_code = t.get("status")
        if recipient != user_id:
            continue
        requester_count += 1
        if unresolved and status_code in (5, 6):
            continue
        items.append({"id": int(tid), "name": t.get("name"), "status_code": status_code, "date": t.get("date"), "date_mod": t.get("date_mod"), "assignee": None})
    logging.info(f"[list_user_tickets] after_requester_filter count={requester_count}")
    logging.info(f"[list_user_tickets] after_unresolved_filter count={len(items)} ids={[it['id'] for it in items[:5]]}")
    if sort == "updated_desc":
        items.sort(key=lambda x: (x.get("date_mod") or ""), reverse=True)
    elif sort == "updated_asc":
        items.sort(key=lambda x: (x.get("date_mod") or ""))
    elif sort == "created_desc":
        items.sort(key=lambda x: (x.get("date") or ""), reverse=True)
    elif sort == "created_asc":
        items.sort(key=lambda x: (x.get("date") or ""))
    total = len(items)
    start = max(0, (int(page) - 1) * int(page_size))
    end = start + int(page_size)
    page_items = items[start:end]
    tickets: list[Dict[str, Any]] = []
    for it in page_items:
        assignee_name = it.get("assignee")
        if assignee_name is None:
            assignee_name = _get_assignee_name(session_token, it["id"])  # lazy resolve only for page items
        tickets.append({"id": it["id"], "name": it["name"], "status": _status_name(int(it["status_code"]) if isinstance(it["status_code"], int) else 0), "date": it["date"], "date_mod": it["date_mod"], "assignee": assignee_name})
    return {"tickets": tickets, "page": int(page), "page_size": int(page_size), "total": int(total)}
def _service_session_token() -> str | None:
    if not settings.glpi_user_token:
        return None
    s = get_session()
    url = f"{_get_api_base()}/initSession"
    try:
        r = s.post(url, json={"user_token": settings.glpi_user_token}, headers=_headers(), timeout=getattr(s, "request_timeout", 10))
        r.raise_for_status()
        j = r.json()
        return j.get("session_token") or j.get("session", {}).get("token") or j.get("session")
    except Exception:
        return None

def search_user_by_email(email: str) -> Dict[str, Any] | None:
    tok = _service_session_token()
    if not tok:
        return None
    s = get_session()
    url = f"{_get_api_base()}/search/User"
    attempts = [
        {"criteria[0][field]": "5", "criteria[0][searchtype]": "equals", "criteria[0][value]": email},
        {"criteria[0][field]": "5", "criteria[0][searchtype]": "contains", "criteria[0][value]": email},
        {"criteria[0][field]": "9", "criteria[0][searchtype]": "contains", "criteria[0][value]": email},
    ]
    for params in attempts:
        params.update({"forcedisplay[0]": "1", "forcedisplay[1]": "2", "forcedisplay[2]": "5"})
        r = s.get(url, params=params, headers=_headers(tok), timeout=getattr(s, "request_timeout", 10))
        if not r.ok:
            continue
        j = r.json()
        data = j.get("data") or j.get("results") or []
        if not data:
            continue
        item = data[0]
        if isinstance(item, dict):
            login = item.get("1") or item.get("name")
            uid = item.get("2") or item.get("id")
            mail = item.get("5") or item.get("email") or email
        elif isinstance(item, list):
            login = (item[1] if len(item) > 1 else None)
            uid = (item[2] if len(item) > 2 else None)
            mail = email
        else:
            continue
        if login:
            return {"login": login, "user_id": uid, "email": mail}
    if not r.ok:
        return None
