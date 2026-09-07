"""Record and summarise data requests."""

from __future__ import annotations

from src.analytics.descriptive import read_sql


def request_history(limit: int = 20):
    return read_sql(
        "SELECT * FROM data_requests ORDER BY requested_at DESC LIMIT ?",
        (limit,),
    )
