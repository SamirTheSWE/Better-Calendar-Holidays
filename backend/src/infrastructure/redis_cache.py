import json
import logging
from dataclasses import asdict
from datetime import date
from json import JSONDecodeError
from typing import Any, cast

from redis.asyncio import Redis

from domain.errors import SourceName
from domain.models import Holiday

logger = logging.getLogger(__name__)


class RedisHolidayCache:
    def __init__(self, *, redis: Redis, key_prefix: str, ttl_days: int) -> None:
        self._redis = redis
        self._key_prefix = key_prefix.strip()
        self._ttl_seconds = max(0, ttl_days * 24 * 60 * 60)

    async def get(
        self,
        *,
        source: SourceName,
        country_code: str,
        year: int,
        region: str | None,
    ) -> list[Holiday] | None:
        key = self._cache_key(source=source, country_code=country_code, year=year, region=region)
        raw = await self._redis.get(key)
        if raw is None:
            logger.debug("Cache miss: %s", key)
            return None

        try:
            payload = cast(dict[str, Any], json.loads(raw))
            holidays_payload = cast(list[dict[str, Any]], payload["holidays"])
            holidays = [
                Holiday(
                    country_code=str(item["country_code"]),
                    country_name=str(item["country_name"]),
                    date=date.fromisoformat(str(item["date"])),
                    name=str(item["name"]),
                    location=str(item["location"]),
                    region_code=str(item["region_code"]) if item.get("region_code") else None,
                )
                for item in holidays_payload
            ]
            logger.debug("Cache hit: %s (%d holidays)", key, len(holidays))
            return holidays
        except (JSONDecodeError, KeyError, TypeError, ValueError):
            logger.warning("Corrupt cache entry, evicting: %s", key)
            await self._redis.delete(key)
            return None

    async def set(
        self,
        *,
        source: SourceName,
        country_code: str,
        year: int,
        region: str | None,
        holidays: list[Holiday],
    ) -> None:
        key = self._cache_key(source=source, country_code=country_code, year=year, region=region)
        payload = {
            "source": source.value,
            "country_code": country_code,
            "year": year,
            "region": region,
            "holidays": [
                {
                    **asdict(item),
                    "date": item.date.isoformat(),
                }
                for item in holidays
            ],
        }
        serialized = json.dumps(payload, separators=(",", ":"))
        if self._ttl_seconds > 0:
            await self._redis.set(key, serialized, ex=self._ttl_seconds)
        else:
            await self._redis.set(key, serialized)
        logger.debug("Cache set: %s (%d holidays)", key, len(holidays))

    def _cache_key(
        self,
        *,
        source: SourceName,
        country_code: str,
        year: int,
        region: str | None,
    ) -> str:
        normalized_region = (region or "national").upper().replace("-", "_")
        return (
            f"{self._key_prefix}:holidays:"
            f"{source.value}:{country_code.upper()}:{year}:{normalized_region}"
        )
