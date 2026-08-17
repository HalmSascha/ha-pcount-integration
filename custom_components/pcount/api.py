"""Async API client for the p-count.de parking occupation endpoint."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

import aiohttp

API_TIMEOUT = 10
DEFAULT_POLLING_FALLBACK = 30


class PCountApiError(Exception):
    """Generic error talking to the p-count API."""


class PCountAuthError(PCountApiError):
    """Raised when authentication fails (401/403)."""


@dataclass
class PCountSection:
    """A single parking section returned by the API."""

    short_name: str
    long_name: str
    occupied_spots: int
    free_spots: int


@dataclass
class PCountData:
    """Full occupation payload for one carpark."""

    measured_at: str
    polling_seconds: int
    sections: list[PCountSection]


class PCountApiClient:
    """Thin async client for the p-count.de occupation JSON endpoint.

    API shape (verified 2026-08-17), e.g. for the Musterfirma carpark:

        GET https://p-count.de/carparks/<carpark_id>/occupation.json
        Authorization: Basic <username>:<password>

        {
          "measured_at": "2026-08-17T13:52:27+00:00",
          "sections": [
            {"short_name": "P3", "long_name": "Parkhaus Nord",
             "occupied_spots": 48, "free_spots": 0},
            {"short_name": "P1+2", "long_name": "Parkhaus Süd",
             "occupied_spots": 176, "free_spots": 151}
          ],
          "polling_seconds": 30
        }

    Every p-count.de customer gets their own carpark_id + credentials, so
    this client is generic and does not hardcode any customer-specific
    values.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        carpark_id: str,
        username: str,
        password: str,
    ) -> None:
        self._session = session
        self._host = host
        self._carpark_id = carpark_id
        self._auth = aiohttp.BasicAuth(username, password)

    @property
    def url(self) -> str:
        """Return the fully qualified occupation endpoint URL."""
        return f"https://{self._host}/carparks/{self._carpark_id}/occupation.json"

    async def async_get_data(self) -> PCountData:
        """Fetch and parse the current occupation data."""
        try:
            async with asyncio.timeout(API_TIMEOUT):
                response = await self._session.get(self.url, auth=self._auth)
                if response.status in (401, 403):
                    raise PCountAuthError(
                        f"Authentication failed ({response.status}) for {self.url}"
                    )
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except PCountAuthError:
            raise
        except (aiohttp.ClientError, TimeoutError) as err:
            raise PCountApiError(f"Error fetching data from {self.url}: {err}") from err

        try:
            sections = [
                PCountSection(
                    short_name=section["short_name"],
                    long_name=section["long_name"],
                    occupied_spots=section["occupied_spots"],
                    free_spots=section["free_spots"],
                )
                for section in payload["sections"]
            ]
            return PCountData(
                measured_at=payload["measured_at"],
                polling_seconds=payload.get("polling_seconds", DEFAULT_POLLING_FALLBACK),
                sections=sections,
            )
        except (KeyError, TypeError) as err:
            raise PCountApiError(f"Unexpected response format: {payload}") from err
