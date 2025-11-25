from flask import Blueprint, request, g
import logging
import re
from html import unescape
from datetime import datetime, timedelta
from ..utils.responses import make_response
from ..services.glpi import get_session, _get_api_base, _headers

bp = Blueprint("glpi_export", __name__)
bp_api = Blueprint("glpi_export_api", __name__)

def _clean_invisible(s: str) -> str:
    return re.sub(r"[\u0000-\u001F\u007F\u200B\u200C\u200D\u2060]", "", s)

def _collapse_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _clean_title(name: str | None) -> str:
    s = (name or "")
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = _collapse_spaces(s)
    s = s.replace('"', '""')
    s = _clean_invisible(s)
    return s.strip()

def _strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "")

def _clean_description(content: str | None) -> str:
    s = unescape(content or "")
    s = _strip_tags(s)
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = _clean_invisible(s)
    s = _collapse_spaces(s)
    if len(s) > 500:
        s = s[:497].rstrip() + "..."
    return s

def _format_date(val: str | None) -> str:
    if not val or str(val).upper() == "NULL":
        return ""
    s = str(val)
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return ""

def _status_text(code: int | None) -> str:
    m = {1: "Novo", 2: "Em andamento (atribuído)", 3: "Em andamento (planejado)", 4: "Pendente", 5: "Solucionado", 6: "Fechado"}
    return m.get(int(code) if isinstance(code, int) else 0, "")

@bp.get("/tickets")
def tickets_export():
    session_token = request.headers.get("Session-Token")
    if not session_token:
        return make_response("error", message="invalid_session", code="invalid_session", http_status=200, request_id=getattr(g, "request_id", None))

    s = get_session()
    base = _get_api_base()
    headers = _headers(session_token)

    periodo = str(request.args.get("periodo", ""))
    page = int(request.args.get("page", 1) or 1)
    page_size_req = int(request.args.get("page_size", 1000) or 1000)
    page_size = max(1, min(1000, page_size_req))

    users = {}
    start = 0
    while True:
        ru = s.get(f"{base}/User", params={"range": f"{start}-{start+999}"}, headers=headers)
        if not ru.ok:
            break
        arr = ru.json() if isinstance(ru.json(), list) else []
        for u in arr:
            uid = u.get("id")
            if uid:
                name = (f"{(u.get('firstname') or '').strip()} {(u.get('realname') or '').strip()}" or (u.get('name') or '')).strip()
                users[int(uid)] = _collapse_spaces(name) if name else (u.get("name") or "")
        if len(arr) < 1000:
            break
        start += 1000

    entities = {}
    re = s.get(f"{base}/Entity", params={"range": "0-1000"}, headers=headers)
    if re.ok:
        for e in re.json() if isinstance(re.json(), list) else []:
            eid = e.get("id")
            if eid:
                entities[int(eid)] = e.get("name") or "Sem Entidade"

    categories = {}
    rc = s.get(f"{base}/ITILCategory", params={"range": "0-1000"}, headers=headers)
    if rc.ok:
        for c in rc.json() if isinstance(rc.json(), list) else []:
            cid = c.get("id")
            if cid:
                categories[int(cid)] = c.get("name") or "Sem Categoria"

    groups = {}
    rg = s.get(f"{base}/Group", params={"range": "0-1000"}, headers=headers)
    if rg.ok:
        for gitem in rg.json() if isinstance(rg.json(), list) else []:
            gid = gitem.get("id")
            if gid:
                groups[int(gid)] = gitem.get("name") or "Sem Grupo"

    all_tickets = []
    start = 0
    while True:
        rt = s.get(f"{base}/Ticket", params={"range": f"{start}-{start+999}", "expand_dropdowns": "false", "get_hateoas": "false"}, headers=headers)
        if not rt.ok:
            break
        batch = rt.json() if isinstance(rt.json(), list) else []
        all_tickets.extend(batch)
        if len(batch) < 1000:
            break
        start += 1000

    req_map = {}
    tech_map = {}
    start = 0
    while True:
        rtu = s.get(f"{base}/Ticket_User", params={"range": f"{start}-{start+49999}"}, headers=headers)
        if not rtu.ok:
            break
        arr = rtu.json() if isinstance(rtu.json(), list) else []
        for tu in arr:
            tid = tu.get("tickets_id")
            if not tid:
                continue
            ttype = tu.get("type")
            uid = tu.get("users_id")
            if ttype == 1 and uid and tid not in req_map:
                req_map[int(tid)] = int(uid)
            if ttype == 2 and uid and tid not in tech_map:
                tech_map[int(tid)] = int(uid)
        if len(arr) < 50000:
            break
        start += 50000

    grp_map = {}
    start = 0
    while True:
        rgt = s.get(f"{base}/Group_Ticket", params={"range": f"{start}-{start+49999}"}, headers=headers)
        if not rgt.ok:
            break
        arr = rgt.json() if isinstance(rgt.json(), list) else []
        for gt in arr:
            tid = gt.get("tickets_id")
            if not tid:
                continue
            if gt.get("type") == 2:
                gid = gt.get("groups_id")
                if gid and tid not in grp_map:
                    grp_map[int(tid)] = int(gid)
        if len(arr) < 50000:
            break
        start += 50000

    items = []
    now = datetime.utcnow()
    cutoff = None
    if periodo == "6m":
        cutoff = now - timedelta(days=180)
    elif periodo == "3m":
        cutoff = now - timedelta(days=90)
    for t in all_tickets:
        tid = t.get("id")
        if not tid:
            continue
        name = _clean_title(t.get("name"))
        desc = _clean_description(t.get("content"))
        status_txt = _status_text(t.get("status"))
        cat = categories.get(int(t.get("itilcategories_id") or 0), "Sem Categoria")
        ent = entities.get(int(t.get("entities_id") or 0), "Sem Entidade")
        req = users.get(req_map.get(int(tid), 0), "Sem Requerente") if req_map.get(int(tid)) else "Sem Requerente"
        tech = users.get(tech_map.get(int(tid), 0), "Não Atribuído") if tech_map.get(int(tid)) else "Não Atribuído"
        grp = groups.get(grp_map.get(int(tid), 0), "Sem Grupo") if grp_map.get(int(tid)) else "Sem Grupo"
        d = t.get("date")
        if cutoff is not None:
            try:
                dt = datetime.strptime(str(d or ""), "%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    dt = datetime.strptime(str(d or ""), "%Y-%m-%d")
                except Exception:
                    dt = None
            if dt and not (cutoff <= dt <= now):
                continue
        items.append({
            "ID": str(tid),
            "Título": name,
            "Descrição": desc,
            "Status": status_txt,
            "Categoria": cat,
            "Entidade": ent,
            "Requerente": req,
            "Técnico": tech,
            "Grupo": grp,
            "Data Criação": _format_date(t.get("date")),
            "Data Modificação": _format_date(t.get("date_mod")),
            "Data Fechamento": _format_date(t.get("closedate")),
            "Tempo Solução (min)": t.get("solve_delay_stat"),
            "Tempo Fechamento (min)": t.get("close_delay_stat"),
        })

    total = len(items)
    start_idx = max(0, (page - 1) * page_size)
    end_idx = start_idx + page_size
    page_items = items[start_idx:end_idx]

    return make_response("ok", data={"meta": {"total": total, "pagina": page, "tamanho_pagina": page_size, "filtro_periodo": (periodo or "")}, "dados": page_items}, http_status=200, request_id=getattr(g, "request_id", None))

@bp_api.get("/glpi-tickets")
def tickets_export_api():
    return tickets_export()