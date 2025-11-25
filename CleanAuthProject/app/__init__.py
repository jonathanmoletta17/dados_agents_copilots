import logging
import time
import uuid
from flask import Flask, g, request

START_TIME = time.time()

def create_app():
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    @app.before_request
    def _reqid_in():
        g.request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

    @app.after_request
    def _reqid_out(resp):
        resp.headers["X-Request-Id"] = getattr(g, "request_id", "")
        return resp

    from .routes.health import bp as health_bp
    from .routes.auth import bp as auth_bp
    from .routes.tickets import bp as tickets_bp
    from .routes.glpi_export import bp as glpi_export_bp
    from .routes.glpi_export import bp_api as glpi_export_api_bp
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(tickets_bp, url_prefix="/api")
    app.register_blueprint(glpi_export_bp, url_prefix="/glpi")
    app.register_blueprint(glpi_export_api_bp, url_prefix="/api")

    app.config["START_TIME"] = START_TIME
    return app
