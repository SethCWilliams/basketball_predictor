"""
Utility functions for timezone handling and date/time conversions.
All data from basketball-reference is in UTC and needs to be converted to user timezone.
"""
from datetime import datetime, date, time
from typing import Optional
import pytz


# Default timezone for the app (Eastern Time - where most NBA operations are based)
DEFAULT_TIMEZONE = 'America/New_York'


def get_user_timezone(tz_string: Optional[str] = None) -> pytz.timezone:
    """
    Get user's timezone, defaulting to Eastern Time.

    Args:
        tz_string: IANA timezone string (e.g., 'America/New_York', 'America/Los_Angeles')

    Returns:
        pytz timezone object
    """
    if tz_string:
        try:
            return pytz.timezone(tz_string)
        except pytz.exceptions.UnknownTimeZoneError:
            pass

    return pytz.timezone(DEFAULT_TIMEZONE)


def utc_to_local(dt: datetime, tz_string: Optional[str] = None) -> datetime:
    """
    Convert UTC datetime to user's local timezone.

    Args:
        dt: datetime object (assumed to be UTC)
        tz_string: User's timezone (defaults to Eastern)

    Returns:
        datetime in user's timezone
    """
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = pytz.UTC.localize(dt)

    user_tz = get_user_timezone(tz_string)
    return dt.astimezone(user_tz)


def format_game_time(dt: datetime, tz_string: Optional[str] = None) -> str:
    """
    Format game time for display (converts UTC to local).

    Args:
        dt: UTC datetime
        tz_string: User's timezone

    Returns:
        Formatted time string (e.g., "7:30 PM EST")
    """
    local_dt = utc_to_local(dt, tz_string)
    time_str = local_dt.strftime("%I:%M %p")  # e.g., "07:30 PM"
    tz_abbr = local_dt.strftime("%Z")  # e.g., "EST" or "EDT"
    return f"{time_str} {tz_abbr}"


def get_current_season_year() -> int:
    """
    Get the current NBA season end year.

    NBA seasons run from October to June, so:
    - Oct 2025 - Jun 2026 = 2025-26 season (season_end_year = 2026)
    - Oct 2026 - Jun 2027 = 2026-27 season (season_end_year = 2027)

    Returns:
        Season end year (e.g., 2026 for 2025-26 season)
    """
    now = datetime.now()
    current_year = now.year

    # If we're in January-September, the season ends this year
    # If we're in October-December, the season ends next year
    if now.month >= 10:
        return current_year + 1
    else:
        return current_year


def get_today_local(tz_string: Optional[str] = None) -> date:
    """
    Get today's date in the user's timezone.

    Args:
        tz_string: User's timezone

    Returns:
        date object in user's timezone
    """
    user_tz = get_user_timezone(tz_string)
    return datetime.now(user_tz).date()


def season_display_name(season_end_year: int) -> str:
    """
    Get display name for a season.

    Args:
        season_end_year: Year the season ends (e.g., 2026)

    Returns:
        Display string (e.g., "2025-26")
    """
    start_year = season_end_year - 1
    return f"{start_year}-{str(season_end_year)[-2:]}"
