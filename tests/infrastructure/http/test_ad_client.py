from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from src.application.exceptions import AdSourceUnavailableError
from src.application.ports.ad_source import AdSnapshot
from src.infrastructure.http.ad_client import AdServiceAdSource


@pytest.mark.asyncio
async def test_get_returns_snapshot_on_200():
    client = AsyncMock(spec=httpx.AsyncClient)
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = {
        "id": 1,
        "title": "Test Ad",
        "description": "Description",
        "price": 100,
        "category": "electronics",
        "city": "Moscow",
        "status": "active",
    }
    client.get.return_value = resp

    ad_source = AdServiceAdSource(client, "http://localhost:8002/")
    snapshot = await ad_source.get(1)

    assert snapshot is not None
    assert isinstance(snapshot, AdSnapshot)
    assert snapshot.ad_id == 1
    assert snapshot.title == "Test Ad"


@pytest.mark.asyncio
async def test_get_returns_none_on_404():
    client = AsyncMock(spec=httpx.AsyncClient)
    resp = Mock()
    resp.status_code = 404
    client.get.return_value = resp

    ad_source = AdServiceAdSource(client, "http://localhost:8002/")
    snapshot = await ad_source.get(1)

    assert snapshot is None


@pytest.mark.asyncio
async def test_get_raises_unavailable_on_500():
    client = AsyncMock(spec=httpx.AsyncClient)
    resp = Mock()
    resp.status_code = 500
    client.get.return_value = resp

    ad_source = AdServiceAdSource(client, "http://localhost:8002/")

    with pytest.raises(AdSourceUnavailableError) as exc_info:
        await ad_source.get(1)

    assert "HTTP 500" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_raises_unavailable_on_network_error():
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.side_effect = httpx.ConnectError("Connection refused")

    ad_source = AdServiceAdSource(client, "http://localhost:8002/")

    with pytest.raises(AdSourceUnavailableError) as exc_info:
        await ad_source.get(1)

    assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_raises_unavailable_on_timeout():
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.side_effect = httpx.TimeoutException("Request timeout")

    ad_source = AdServiceAdSource(client, "http://localhost:8002/")

    with pytest.raises(AdSourceUnavailableError) as exc_info:
        await ad_source.get(1)

    assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_raises_unavailable_on_4xx_other_than_404():
    client = AsyncMock(spec=httpx.AsyncClient)
    resp = Mock()
    resp.status_code = 403
    client.get.return_value = resp

    ad_source = AdServiceAdSource(client, "http://localhost:8002/")

    with pytest.raises(AdSourceUnavailableError) as exc_info:
        await ad_source.get(1)

    assert "HTTP 403" in str(exc_info.value)
