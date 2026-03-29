from datetime import UTC, datetime
from typing import Any, cast

from redis.asyncio import Redis

from domain.errors import CalendarificQuotaExceededError


class CalendarificQuota:
    def __init__(self, *, redis: Redis, key_prefix: str, monthly_limit: int) -> None:
        self._redis = redis
        self._monthly_limit = monthly_limit
        self._key_prefix = key_prefix

    async def try_consume(self) -> bool:
        """Attempt to consume one quota unit. Returns True on success, False if exhausted."""
        month_utc = _utc_month()
        quota_key = self._monthly_quota_key(month_utc=month_utc)
        ttl_seconds = _seconds_until_next_month()

        result = await cast(
            Any,
            self._redis.eval(
                """
            local quota_key = KEYS[1]
            local quota_limit = tonumber(ARGV[1])
            local key_ttl = tonumber(ARGV[2])

            local used = tonumber(redis.call("GET", quota_key) or "0")
            if used >= quota_limit then
                return 0
            end

            redis.call("INCR", quota_key)

            if redis.call("TTL", quota_key) < 0 then
                redis.call("EXPIRE", quota_key, key_ttl)
            end

            return 1
            """,
                1,
                quota_key,
                str(self._monthly_limit),
                str(ttl_seconds),
            ),
        )
        return int(result) == 1

    async def raise_if_exhausted(self, *, month_utc: str | None = None) -> None:
        """Raise CalendarificQuotaExceededError with current usage info."""
        month = month_utc or _utc_month()
        quota_key = self._monthly_quota_key(month_utc=month)
        used_raw = await self._redis.get(quota_key)
        used = int(used_raw) if used_raw is not None else 0
        raise CalendarificQuotaExceededError(
            used=used,
            limit=self._monthly_limit,
            month_utc=month,
        )

    def _monthly_quota_key(self, *, month_utc: str) -> str:
        return f"{self._key_prefix}:calendarific:quota:{month_utc}"


def _utc_month() -> str:
    return datetime.now(UTC).strftime("%Y-%m")


def _seconds_until_next_month() -> int:
    now = datetime.now(UTC)
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1, tzinfo=UTC)
    else:
        next_month = datetime(now.year, now.month + 1, 1, tzinfo=UTC)
    return int((next_month - now).total_seconds())
