#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

import math
from datetime import datetime


def parse_duration(s: str) -> int:
    duration_format = "%H:%M:%S"
    # We have to make this akward split by 'd' as the transport API returns some weird timestamps
    duration = datetime.strptime(s.split("d")[1], duration_format) - datetime.strptime(
        "00:00:00", duration_format
    )
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{math.floor(hours)}h")
    if minutes > 0:
        parts.append(f"{math.floor(minutes)}min")
    if seconds > 0:
        parts.append(f"{math.floor(seconds)}s")

    return " ".join(parts)


def prase_date(s: str) -> str:
    datetime_obj = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
    return datetime_obj.strftime("%Y-%m-%d %H:%M")


def parse_procent(d) -> str:
    return str(round(d * 100)) + "%"


# See https://stackoverflow.com/a/60124334 for sources
def clean_nones(value):
    """
    Recursively remove all None values from dictionaries and lists, and returns
    the result as a new dictionary or list.
    """
    if isinstance(value, list):
        return [clean_nones(x) for x in value if x is not None]
    elif isinstance(value, dict):
        return {key: clean_nones(val) for key, val in value.items() if val is not None}
    else:
        return value
