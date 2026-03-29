from http import HTTPStatus
from typing import Any


def success_response(
    *,
    code: int = 200,
    status: str = "OK",
    detail: dict[str, Any],
) -> dict[str, Any]:
    return {
        "code": code,
        "status": status,
        "detail": detail,
    }


def error_response(
    *,
    code: int,
    status: str | None = None,
    message: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    default_status = _default_status(code)
    return {
        "code": code,
        "status": status or default_status,
        "detail": {
            "message": message,
            **(detail or {}),
        },
    }


def _default_status(code: int) -> str:
    try:
        return HTTPStatus(code).phrase
    except ValueError:
        return "Error"
