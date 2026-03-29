from typing import NoReturn

from fastapi import HTTPException

from domain.errors import (
    CalendarificQuotaExceededError,
    MissingCalendarificKeyError,
    SourceUnavailableError,
)


def raise_mapped_http_exception(*, exc: Exception, country_code: str) -> NoReturn:
    country_code_upper = country_code.upper()

    if isinstance(exc, KeyError):
        raise HTTPException(
            status_code=404,
            detail={
                "status": "Country NOT Supported",
                "message": (f"Country {country_code_upper} Is NOT Supported for this endpoint."),
            },
        ) from exc

    if isinstance(exc, MissingCalendarificKeyError):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "Configuration Required",
                "message": str(exc),
            },
        ) from exc

    if isinstance(exc, SourceUnavailableError):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "Source Unavailable",
                "message": str(exc),
            },
        ) from exc

    if isinstance(exc, CalendarificQuotaExceededError):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "Calendarific Quota Reached",
                "message": str(exc),
                "quota_limit": exc.limit,
                "quota_used": exc.used,
                "month_utc": exc.month_utc,
            },
        ) from exc

    raise exc
