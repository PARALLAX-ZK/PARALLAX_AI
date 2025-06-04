import datetime
import pytz
from typing import Optional

UTC = pytz.UTC
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def get_utc_now() -> datetime.datetime:
    """
    Returns the current UTC timestamp as a datetime object.
    """
    return datetime.datetime.now(UTC)

def format_iso8601(dt: datetime.datetime) -> str:
    """
    Formats a datetime object as ISO-8601 string (UTC).
    """
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    return dt.strftime(ISO_FORMAT)

def parse_iso8601(ts: str) -> datetime.datetime:
    """
    Parses ISO-8601 formatted string back into a datetime object.
    """
    return datetime.datetime.strptime(ts, ISO_FORMAT).replace(tzinfo=UTC)

def timestamp_for_blockchain() -> int:
    """
    Returns current UTC timestamp as a UNIX integer for onchain compatibility.
    """
    return int(get_utc_now().timestamp())

def human_readable(dt: Optional[datetime.datetime] = None) -> str:
    """
    Converts a datetime object (or now) into a human-readable format.
    """
    if dt is None:
        dt = get_utc_now()
    return dt.strftime("%A, %B %d %Y %H:%M:%S UTC")

def seconds_since(ts: datetime.datetime) -> int:
    """
    Returns the number of seconds since the given timestamp.
    """
    now = get_utc_now()
    delta = now - ts
    return int(delta.total_seconds())

def is_fresh(ts: datetime.datetime, threshold_seconds: int = 60) -> bool:
    """
    Checks if the given timestamp is within the freshness threshold.
    Useful for validating inference or DACert timestamps.
    """
    return seconds_since(ts) <= threshold_seconds

# Example usage
if __name__ == "__main__":
    now = get_utc_now()
    iso = format_iso8601(now)
    parsed = parse_iso8601(iso)
    unix = timestamp_for_blockchain()

    print("Current UTC:", now)
    print("ISO-8601:", iso)
    print("Parsed ISO:", parsed)
    print("UNIX Timestamp:", unix)
    print("Human-readable:", human_readable())
    print("Fresh (<= 60s):", is_fresh(parsed))
