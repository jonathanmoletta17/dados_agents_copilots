import os
import json
import urllib.request
import urllib.parse

GLPI_URL = os.environ.get("GLPI_URL", "")
GLPI_APP_TOKEN = os.environ.get("GLPI_APP_TOKEN", "")
GLPI_USER_TOKEN = os.environ.get("GLPI_USER_TOKEN", "")

def _ensure_env():
    if not os.environ.get("GLPI_URL", ""):
        p = r"C:\\Users\\jonathan-moletta\\OneDrive - Governo do Estado do Rio Grande do Sul\\Área de Trabalho\\BD_cau_sis\\bd_cau\\.env"
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass

def _get_base_url():
    v = os.environ.get("GLPI_URL", "")
    if v:
        return v
    p = r"C:\\Users\\jonathan-moletta\\OneDrive - Governo do Estado do Rio Grande do Sul\\Área de Trabalho\\BD_cau_sis\\bd_cau\\.env"
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("GLPI_URL="):
                        return line.split("=",1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return ""

def _headers(session_token: str = None):
    h = {"Content-Type":"application/json"}
    app = os.environ.get("GLPI_APP_TOKEN", "")
    if app:
        h["App-Token"] = app
    if session_token:
        h["Session-Token"] = session_token
    else:
        user = os.environ.get("GLPI_USER_TOKEN", "")
        if user:
            h["Authorization"] = f"user_token {user}"
    return h

def init_session():
    _ensure_env()
    base = _get_base_url()
    if not base:
        return None
    req = urllib.request.Request(base.rstrip("/")+"/initSession", headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("session_token")

def kill_session(session_token: str):
    try:
        _ensure_env()
        base = _get_base_url()
        req = urllib.request.Request(base.rstrip("/")+"/killSession", headers=_headers(session_token))
        urllib.request.urlopen(req, timeout=15).read()
    except Exception:
        pass

def fetch_tickets(session_token: str, modified_since: str = None, include_deleted: bool = True, range_start: int = 0, range_len: int = 500):
    _ensure_env()
    base_url = _get_base_url()
    base = base_url.rstrip("/")+"/Ticket"
    qs = {
        "range": f"{range_start}-{range_start+range_len-1}",
        "expand_dropdowns": "1",
    }
    if not include_deleted:
        qs["is_deleted"] = "0"
    url = base+"?"+urllib.parse.urlencode(qs)
    req = urllib.request.Request(url, headers=_headers(session_token))
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data if isinstance(data, list) else []

def fetch_all(session_token: str, include_deleted: bool = True):
    out = []
    start = 0
    while True:
        chunk = fetch_tickets(session_token, include_deleted=include_deleted, range_start=start)
        if not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 500:
            break
        start += 500
    return out

def list_search_options(session_token: str, itemtype: str = "Ticket"):
    _ensure_env()
    base = _get_base_url()
    url = base.rstrip("/")+f"/listSearchOptions/{itemtype}"
    req = urllib.request.Request(url, headers=_headers(session_token))
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data if isinstance(data, list) else []

def _get_field_id(opts, name):
    for o in opts:
        if str(o.get("field")) == name:
            return int(o.get("id"))
    return None

def _status_text(v):
    try:
        n = int(str(v))
    except Exception:
        return str(v or '')
    return {
        1: 'novo',
        2: 'processando (atribuído)',
        3: 'processando (planejado)',
        4: 'pendente',
        5: 'solucionado',
        6: 'fechado'
    }.get(n, str(v))

USER_CACHE = {}

def _user_name(session_token: str, uid):
    if uid in (None, '', 0, '0'):
        return ''
    
    # Handle list of IDs (e.g. multiple technicians)
    if isinstance(uid, list):
        names = []
        for u in uid:
            n = _user_name(session_token, u)
            if n:
                names.append(n)
        return ", ".join(names)

    # If it's already a name (not a digit), return it
    s_uid = str(uid)
    if not s_uid.isdigit():
        return s_uid

    # Check cache
    if s_uid in USER_CACHE:
        return USER_CACHE[s_uid]

    try:
        base = _get_base_url()
        url = base.rstrip("/")+f"/User/{s_uid}"
        req = urllib.request.Request(url, headers=_headers(session_token))
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            name = (data.get('realname') or data.get('name') or '')
            if name:
                USER_CACHE[s_uid] = name
            return name
    except Exception:
        return ''

def search_tickets(session_token: str, include_deleted: bool = True, range_start: int = 0, range_len: int = 500):
    _ensure_env()
    opts = list_search_options(session_token, "Ticket")
    fields = {
        "id": _get_field_id(opts, "id"),
        "name": _get_field_id(opts, "name"),
        "content": _get_field_id(opts, "content"),
        "status": _get_field_id(opts, "status"),
        "itilcategories_id": _get_field_id(opts, "itilcategories_id"),
        "entities_id": _get_field_id(opts, "entities_id"),
        "users_id_recipient": _get_field_id(opts, "users_id_recipient"),
        "users_id_assign": _get_field_id(opts, "users_id_assign"),
        "groups_id_assign": _get_field_id(opts, "groups_id_assign"),
        "date": _get_field_id(opts, "date"),
        "date_mod": _get_field_id(opts, "date_mod"),
        "is_deleted": _get_field_id(opts, "is_deleted")
    }
    defaults = {"id":2,"name":1,"content":95,"status":12,"entities_id":80,"itilcategories_id":7,"date":15,"date_mod":19}
    for k,v in defaults.items():
        if fields.get(k) is None:
            fields[k] = v
    forced = [v for v in fields.values() if v is not None]
    base_url = _get_base_url()
    base = base_url.rstrip("/")+"/search/Ticket"
    
    def _do_query(del_flag):
        qs = {
            "range": f"{range_start}-{range_start+range_len-1}",
        }
        for fid in forced:
            qs.setdefault("forcedisplay[]", []).append(fid)
        
        # Explicitly set is_deleted
        qs["is_deleted"] = "1" if del_flag else "0"
            
        url = base+"?"+urllib.parse.urlencode(qs, doseq=True)
        req = urllib.request.Request(url, headers=_headers(session_token))
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("data") or []
            out = []
            for r in rows:
                f = r
                # If we requested is_deleted=0, double check the field if present
                row_is_deleted = f.get(str(fields['is_deleted']))
                if not del_flag and row_is_deleted == 1:
                     continue # Skip if API returned a deleted ticket when we didn't want one

                out.append({
                    'ID': f.get(str(fields['id'])) or f.get('2') or r.get("id") or 0,
                    'TITULO': f.get(str(fields['name'])) or f.get('1') or '',
                    'DESCRICAO': f.get(str(fields['content'])) or f.get('95') or '',
                    'STATUS': _status_text(f.get(str(fields['status'])) or f.get('12') or ''),
                    'CATEGORIA': f.get(str(fields['itilcategories_id'])) or f.get('7') or '',
                    'ENTIDADE': f.get(str(fields['entities_id'])) or f.get('80') or '',
                    'REQUERENTE': _user_name(session_token, f.get(str(fields['users_id_recipient']))),
                    'TECNICO': _user_name(session_token, f.get(str(fields['users_id_assign']))),
                    'GRUPO': f.get(str(fields['groups_id_assign'])) or '',
                    'DATA_CRIACAO': f.get(str(fields['date'])) or f.get('15') or '',
                    'DATA_MODIFICACAO': f.get(str(fields['date_mod'])) or f.get('19') or '',
                    'IS_DELETED': 1 if del_flag else 0
                })
            return out

    if include_deleted:
        return _do_query(False) + _do_query(True)
    return _do_query(False)

def search_tickets_all(session_token: str, include_deleted: bool = False, range_len: int = 500):
    out = []
    start = 0
    while True:
        chunk = search_tickets(session_token, include_deleted=include_deleted, range_start=start, range_len=range_len)
        if not chunk:
            break
        out.extend(chunk)
        if len(chunk) < range_len:
            break
        start += range_len
    return out

def search_tickets_by_text(session_token: str, q: str, range_start: int = 0, range_len: int = 50):
    _ensure_env()
    opts = list_search_options(session_token, "Ticket")
    fields = {
        "id": _get_field_id(opts, "id"),
        "name": _get_field_id(opts, "name"),
        "content": _get_field_id(opts, "content"),
        "status": _get_field_id(opts, "status"),
        "itilcategories_id": _get_field_id(opts, "itilcategories_id"),
        "entities_id": _get_field_id(opts, "entities_id"),
        "users_id_recipient": _get_field_id(opts, "users_id_recipient"),
        "users_id_assign": _get_field_id(opts, "users_id_assign"),
        "groups_id_assign": _get_field_id(opts, "groups_id_assign"),
        "date": _get_field_id(opts, "date"),
        "date_mod": _get_field_id(opts, "date_mod"),
        "is_deleted": _get_field_id(opts, "is_deleted")
    }
    defaults = {"id":2,"name":1,"content":95,"status":12,"entities_id":80,"itilcategories_id":7,"date":15,"date_mod":19}
    for k,v in defaults.items():
        if fields.get(k) is None:
            fields[k] = v
    forced = [v for v in fields.values() if v is not None]
    base_url = _get_base_url()
    base = base_url.rstrip("/")+"/search/Ticket"
    params = []
    params.append(("range", f"{range_start}-{range_start+range_len-1}"))
    for fid in forced:
        params.append(("forcedisplay[]", fid))
    params.append(("is_deleted", "0"))
    if q and q.strip():
        if fields["name"] is not None:
            params.append(("criteria[0][field]", fields["name"]))
            params.append(("criteria[0][searchtype]", "contains"))
            params.append(("criteria[0][value]", q))
        if fields["content"] is not None:
            params.append(("criteria[1][link]", "OR"))
            params.append(("criteria[1][field]", fields["content"]))
            params.append(("criteria[1][searchtype]", "contains"))
            params.append(("criteria[1][value]", q))
    if fields["date_mod"] is not None:
        params.append(("sort", fields["date_mod"]))
        params.append(("order", "DESC"))
    url = base+"?"+urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers=_headers(session_token))
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        rows = data.get("data") or []
        out = []
        for r in rows:
            f = r
            out.append({
                'ID': f.get(str(fields['id'])) or f.get('2') or r.get("id") or 0,
                'TITULO': f.get(str(fields['name'])) or f.get('1') or '',
                'DESCRICAO': f.get(str(fields['content'])) or f.get('95') or '',
                'STATUS': _status_text(f.get(str(fields['status'])) or f.get('12') or ''),
                'CATEGORIA': f.get(str(fields['itilcategories_id'])) or f.get('7') or '',
                'ENTIDADE': f.get(str(fields['entities_id'])) or f.get('80') or '',
                'REQUERENTE': _user_name(session_token, f.get(str(fields['users_id_recipient']))),
                'TECNICO': _user_name(session_token, f.get(str(fields['users_id_assign']))),
                'GRUPO': f.get(str(fields['groups_id_assign'])) or '',
                'DATA_CRIACAO': f.get(str(fields['date'])) or f.get('15') or '',
                'DATA_MODIFICACAO': f.get(str(fields['date_mod'])) or f.get('19') or '',
                'IS_DELETED': f.get(str(fields['is_deleted'])) if fields['is_deleted'] is not None else 0
            })
        return out

def get_deleted_ids(session_token: str):
    _ensure_env()
    base_url = _get_base_url()
    base = base_url.rstrip("/")+"/search/Ticket"
    ids = set()
    start = 0
    while True:
        qs = {"range": f"{start}-{start+499}", "is_deleted": "1"}
        url = base+"?"+urllib.parse.urlencode(qs)
        req = urllib.request.Request(url, headers=_headers(session_token))
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("data") or []
            for r in rows:
                rid = r.get("id")
                if rid is not None:
                    ids.add(int(rid))
            if len(rows) < 500:
                break
            start += 500
    return ids

def get_ticket(session_token: str, ticket_id: int):
    _ensure_env()
    base = _get_base_url()
    url = base.rstrip("/")+f"/Ticket/{ticket_id}"
    req = urllib.request.Request(url, headers=_headers(session_token))
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data if isinstance(data, dict) else {}