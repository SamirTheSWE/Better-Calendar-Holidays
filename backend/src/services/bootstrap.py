import logging
from typing import Any

from config import (
    CALENDARIFIC_BASE_URL,
    CALENDARIFIC_MONTHLY_LIMIT,
    NAGER_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
    Settings,
)
from domain.errors import CalendarificQuotaExceededError, SourceName, SourceUnavailableError
from domain.interfaces import CountryHolidaySource
from infrastructure.calendarific import CalendarificClient
from infrastructure.nager import NagerClient
from infrastructure.quota import CalendarificQuota
from infrastructure.quota_gated import QuotaGatedSource
from infrastructure.redis_cache import RedisHolidayCache
from services.holiday_service import HolidayService
from services.registry import CountryRegistry

logger = logging.getLogger(__name__)


async def build_service(*, settings: Settings, redis: Any) -> HolidayService:
    nager = NagerClient(
        base_url=NAGER_BASE_URL,
        timeout_seconds=REQUEST_TIMEOUT_SECONDS,
    )

    if not settings.calendarific_api_key:
        raise RuntimeError("CALENDARIFIC_API_KEY is required. Set it in backend/.env.")

    quota = CalendarificQuota(
        redis=redis,
        key_prefix=settings.redis_key_prefix,
        monthly_limit=CALENDARIFIC_MONTHLY_LIMIT,
    )
    calendarific_http = CalendarificClient(
        api_key=settings.calendarific_api_key,
        base_url=CALENDARIFIC_BASE_URL,
        timeout_seconds=REQUEST_TIMEOUT_SECONDS,
    )
    calendarific = QuotaGatedSource(source=calendarific_http, quota=quota)

    try:
        logger.info("Fetching Calendarific country list...")
        calendarific_countries = await calendarific.list_countries()
    except CalendarificQuotaExceededError as exc:
        raise RuntimeError(
            "Failed to initialize Calendarific countries: monthly quota reached "
            f"({exc.used}/{exc.limit}) for {exc.month_utc}."
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize Calendarific countries. Check CALENDARIFIC_API_KEY."
        ) from exc

    try:
        logger.info("Fetching Nager country list...")
        nager_countries = await nager.list_countries()
    except SourceUnavailableError as exc:
        raise RuntimeError("Failed to initialize Nager countries.") from exc

    registry = await CountryRegistry.build(
        nager_countries=nager_countries,
        calendarific_countries=calendarific_countries,
    )
    logger.info(
        "Country registry built: %d countries (%d Nager, %d Calendarific)",
        len(registry.list_countries()),
        len(nager_countries),
        len(calendarific_countries),
    )

    cache = RedisHolidayCache(
        redis=redis,
        key_prefix=settings.redis_key_prefix,
        ttl_days=settings.cache_ttl_days,
    )

    sources: dict[SourceName, CountryHolidaySource] = {
        SourceName.NAGER: nager,
        SourceName.CALENDARIFIC: calendarific,
    }

    return HolidayService(
        sources=sources,
        cache=cache,
        registry=registry,
    )
