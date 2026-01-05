from __future__ import annotations

from typing import Iterable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_retrying_session(
    *,
    max_retries: int,
    backoff_factor: float,
    status_forcelist: Iterable[int] = (429, 500, 502, 503, 504),
    allowed_methods: Optional[Iterable[str]] = None,
) -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=max_retries,
        connect=max_retries,
        read=max_retries,
        status=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=tuple(status_forcelist),
        allowed_methods=frozenset(
            m.upper()
            for m in (
                allowed_methods
                or ("HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            )
        ),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

