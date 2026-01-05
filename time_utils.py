from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional, Union


def parse_datetime(value: str) -> datetime:
    raw = value.strip()
    if not raw:
        raise ValueError("empty datetime string")

    normalized = raw.replace("Z", "+00:00")
    if "T" in normalized and " " not in normalized:
        normalized = normalized.replace("T", " ")

    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def to_utc_datetime(value: Union[str, datetime]) -> datetime:
    dt = parse_datetime(value) if isinstance(value, str) else value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_sqlite_datetime(value: Union[str, datetime], *, timespec: str = "seconds") -> str:
    dt = to_utc_datetime(value).replace(tzinfo=None)
    return dt.isoformat(sep=" ", timespec=timespec)


def format_sqlite_date(value: Union[str, date, datetime]) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    raw = str(value).strip()
    if not raw:
        raise ValueError("empty date string")

    # Accept YYYY-MM-DD or a datetime-like string.
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]

    return parse_datetime(raw).date().isoformat()


def maybe_format_sqlite_datetime(value: Optional[Union[str, datetime]]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return format_sqlite_datetime(value)
