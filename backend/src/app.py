import logging
import logging.config
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import from_url
from redis.exceptions import RedisError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.envelope import error_response
from config import APP_NAME, settings
from rate_limit import limiter
from routes.calendar import router as calendar_router
from routes.meta import router as meta_router
from services.bootstrap import build_service

_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not settings.redis_url:
        raise RuntimeError("REDIS_URL is required. Set it in backend/.env.")

    redis = cast(
        Any,
        from_url(settings.redis_url, encoding="utf-8", decode_responses=True),
    )
    try:
        await redis.ping()
        logger.info("Redis connection established.")
    except RedisError as exc:
        await redis.aclose()
        raise RuntimeError("Failed to connect to Redis. Check REDIS_URL.") from exc

    service = await build_service(settings=settings, redis=redis)
    app.state.service = service
    logger.info("Service ready.")

    yield
    await redis.aclose()
    logger.info("Redis connection closed.")


def create_app() -> FastAPI:
    allowed_origins = [
        origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()
    ]
    app_instance = FastAPI(title=APP_NAME, lifespan=lifespan)
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )
    app_instance.state.limiter = limiter
    app_instance.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app_instance.include_router(meta_router, prefix="/api")
    app_instance.include_router(calendar_router, prefix="/api")
    _register_exception_handlers(app_instance)
    return app_instance


def _register_exception_handlers(app_instance: FastAPI) -> None:
    @app_instance.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        extra: dict[str, Any]
        if isinstance(detail, dict):
            status = str(detail.get("status", "Error"))
            message = str(detail.get("message", "Request failed."))
            extra = {
                key: value for key, value in detail.items() if key not in {"status", "message"}
            }
        else:
            status = "Error"
            message = str(detail)
            extra = {}

        payload = error_response(
            code=exc.status_code,
            status=status,
            message=message,
            detail=extra,
        )
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app_instance.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        payload = error_response(
            code=422,
            status="Validation Failed",
            message="Request validation failed.",
            detail={"errors": exc.errors()},
        )
        return JSONResponse(status_code=422, content=payload)

    @app_instance.exception_handler(Exception)
    async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        payload = error_response(
            code=500,
            status="Internal Server Error",
            message="An unexpected error occurred.",
            detail={"exception_type": exc.__class__.__name__},
        )
        return JSONResponse(status_code=500, content=payload)


app = create_app()
