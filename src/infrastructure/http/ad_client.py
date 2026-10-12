import logging
import urllib.parse

import httpx

from src.application.exceptions import AdSourceUnavailableError
from src.application.ports.ad_source import AdSnapshot, AdSource
from src.infrastructure.tracing.context import get_trace_id

logger = logging.getLogger(__name__)


class AdServiceAdSource(AdSource):
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def get(self, ad_id: int) -> AdSnapshot | None:
        url = urllib.parse.urljoin(self._base_url, f"internal/ads/{ad_id}")
        headers = {}
        trace_id = get_trace_id()
        if trace_id:
            headers["X-Trace-Id"] = trace_id
        try:
            resp = await self._client.get(url, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("ad source unavailable for ad %s: %s", ad_id, exc)
            raise AdSourceUnavailableError(
                f"Network error fetching ad {ad_id}: {exc}"
            ) from exc

        if resp.status_code == 404:
            return None

        if resp.status_code != 200:
            logger.warning("ad source returned %s for ad %s", resp.status_code, ad_id)
            raise AdSourceUnavailableError(
                f"HTTP {resp.status_code} fetching ad {ad_id}"
            )

        data = resp.json()
        return AdSnapshot(
            ad_id=data["id"],
            title=data["title"],
            description=data["description"],
            price=data["price"],
            category=data["category"],
            city=data["city"],
            status=data["status"],
        )
