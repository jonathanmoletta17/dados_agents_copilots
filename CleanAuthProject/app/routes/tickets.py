from flask import Blueprint, request, g
from ..utils.responses import make_response
from ..services.glpi import create_ticket as glpi_create_ticket
from ..services import glpi

bp = Blueprint("tickets", __name__)

@bp.post("/create-ticket")
def create():
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    description = (body.get("description") or "").strip()
    category_id = body.get("category_id")
    requesttype_id = body.get("requesttype_id")
    type_ = body.get("type", 1)
    status_ = body.get("status", 2)
    session_token = request.headers.get("Session-Token")
    if not session_token:
        return make_response("error", message="invalid_session", code="invalid_session", http_status=200, request_id=getattr(g, "request_id", None))
    if not title or not description or not isinstance(category_id, int):
        return make_response("error", message="title, description e category_id são obrigatórios", code="bad_request", http_status=422, request_id=getattr(g, "request_id", None))
    try:
        ticket = glpi_create_ticket(session_token=session_token, title=title, description=description, category_id=category_id, requesttype_id=requesttype_id, type_=type_, status=status_)
        if not ticket.get("ok"):
            return make_response("error", message="glpi_unavailable", code="glpi_unavailable", http_status=200, request_id=getattr(g, "request_id", None))
        return make_response("ok", data={"ticket_id": ticket.get("id"), "title": ticket.get("name"), "description": description, "category_id": category_id}, http_status=200, request_id=getattr(g, "request_id", None))
    except PermissionError:
        return make_response("error", message="invalid_session", code="invalid_session", http_status=200, request_id=getattr(g, "request_id", None))
    except Exception:
        return make_response("error", message="glpi_unavailable", code="glpi_unavailable", http_status=200, request_id=getattr(g, "request_id", None))

@bp.get("/list-user-tickets")
def list_user_tickets():
    session_token = request.headers.get("Session-Token")
    if not session_token:
        return make_response("error", message="invalid_session", code="invalid_session", http_status=200, request_id=getattr(g, "request_id", None))

    q_unresolved = str(request.args.get("unresolved", "true")).strip().lower()
    unresolved = q_unresolved in {"1", "true", "yes", "y", "on"}

    q_page = request.args.get("page", "1")
    q_page_size = request.args.get("page_size", "10")
    try:
        page = int(q_page)
        page_size = int(q_page_size)
    except ValueError:
        return make_response("error", message="invalid_pagination", code="invalid_pagination", http_status=200, request_id=getattr(g, "request_id", None))

    sort = str(request.args.get("sort", "updated_desc")).strip().lower()
    if sort not in {"updated_desc", "updated_asc", "created_desc", "created_asc"}:
        sort = "updated_desc"

    try:
        data = glpi.list_user_tickets(session_token=session_token, unresolved=unresolved, page=page, page_size=page_size, sort=sort)
        return make_response("ok", data=data, http_status=200, request_id=getattr(g, "request_id", None))
    except PermissionError:
        return make_response("error", message="invalid_session", code="invalid_session", http_status=200, request_id=getattr(g, "request_id", None))
    except RuntimeError as e:
        msg = str(e)
        if msg == "glpi_unavailable":
            return make_response("error", message="glpi_unavailable", code="glpi_unavailable", http_status=200, request_id=getattr(g, "request_id", None))
        return make_response("error", message="internal_error", code="internal_error", http_status=200, request_id=getattr(g, "request_id", None))
    except Exception:
        return make_response("error", message="internal_error", code="internal_error", http_status=200, request_id=getattr(g, "request_id", None))
