import json
from flask import Response


def make_response(
    status: str,
    data=None,
    message: str | None = None,
    code: str | None = None,
    http_status: int = 200,
    request_id: str | None = None,
):
    payload = {"status": status}
    if message is not None:
        payload["message"] = message
    if code is not None:
        payload["code"] = code
    if data is not None:
        payload["data"] = data
    if request_id is not None:
        payload["request_id"] = request_id
    return Response(json.dumps(payload, ensure_ascii=False), status=http_status, content_type="application/json; charset=utf-8")
