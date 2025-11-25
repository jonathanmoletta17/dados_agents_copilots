import time
from flask import Blueprint, g, current_app
from config import settings
from ..utils.responses import make_response

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    uptime = int(time.time() - (current_app.config.get("START_TIME", time.time())))
    flags = {"glpi_url_configured": bool(settings.glpi_url), "app_token_configured": bool(settings.glpi_app_token), "user_token_configured": bool(settings.glpi_user_token)}
    return make_response("ok", data={"version": "1.0.0", "uptime": uptime, **flags}, request_id=getattr(g, "request_id", None), http_status=200)
