from flask import Blueprint, request, g
import requests
from ..utils.responses import make_response

bp = Blueprint("auth", __name__)

@bp.post("/authenticate-user")
def authenticate_user():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    user_token = body.get("user_token")
    if not user_token:
        if not email or not password:
            return make_response("error", message="email e password são obrigatórios", code="bad_request", http_status=400, request_id=getattr(g, "request_id", None))
    from ..services.glpi import authenticate_user, authenticate_with_user_token
    try:
        if user_token:
            auth = authenticate_with_user_token(user_token)
        else:
            auth = authenticate_user(email, password)
        data = {"session_token": auth["session_token"], "user_id": auth.get("user_id"), "login": auth.get("login"), "email": auth.get("email", email)}
        return make_response("ok", data=data, http_status=200, request_id=getattr(g, "request_id", None))
    except PermissionError:
        return make_response("error", message="invalid_credentials", code="invalid_credentials", http_status=200, request_id=getattr(g, "request_id", None))
    except RuntimeError:
        return make_response("error", message="glpi_unavailable", code="glpi_unavailable", http_status=200, request_id=getattr(g, "request_id", None))
    except requests.exceptions.RequestException:
        return make_response("error", message="glpi_unavailable", code="glpi_unavailable", http_status=200, request_id=getattr(g, "request_id", None))
    except Exception:
        return make_response("error", message="glpi_unavailable", code="glpi_unavailable", http_status=200, request_id=getattr(g, "request_id", None))
