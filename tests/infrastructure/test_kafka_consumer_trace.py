from unittest.mock import AsyncMock, Mock

import pytest

from src.infrastructure.messaging.kafka_ads_consumer import KafkaAdsConsumer
from src.infrastructure.tracing.context import get_trace_id, set_trace_id


@pytest.mark.asyncio
async def test_extract_trace_id_from_headers():
    consumer = KafkaAdsConsumer(
        consumer=Mock(),
        index_ad=AsyncMock(),
        remove_ad=AsyncMock(),
    )

    headers = [("trace-id", b"test-trace-123"), ("other", b"value")]
    trace_id = consumer._extract_trace_id(headers)
    assert trace_id == "test-trace-123"


@pytest.mark.asyncio
async def test_extract_trace_id_handles_missing_header():
    consumer = KafkaAdsConsumer(
        consumer=Mock(),
        index_ad=AsyncMock(),
        remove_ad=AsyncMock(),
    )

    headers = [("other", b"value")]
    trace_id = consumer._extract_trace_id(headers)
    assert trace_id is None


@pytest.mark.asyncio
async def test_extract_trace_id_handles_none_headers():
    consumer = KafkaAdsConsumer(
        consumer=Mock(),
        index_ad=AsyncMock(),
        remove_ad=AsyncMock(),
    )

    trace_id = consumer._extract_trace_id(None)
    assert trace_id is None


@pytest.mark.asyncio
async def test_process_message_sets_and_resets_trace_id():
    index_ad = AsyncMock()
    consumer = KafkaAdsConsumer(
        consumer=Mock(),
        index_ad=index_ad,
        remove_ad=AsyncMock(),
    )

    msg = Mock()
    msg.headers = [("trace-id", b"kafka-trace-456")]
    msg.value = {"event": "ad.created", "payload": {"ad_id": 42}}

    initial_trace = "initial-trace"
    set_trace_id(initial_trace)

    await consumer._process_message(msg)

    assert get_trace_id() == initial_trace
    index_ad.execute.assert_called_once_with(42)


@pytest.mark.asyncio
async def test_process_message_handles_exception_and_resets_trace_id():
    index_ad = AsyncMock(side_effect=RuntimeError("test error"))
    consumer = KafkaAdsConsumer(
        consumer=Mock(),
        index_ad=index_ad,
        remove_ad=AsyncMock(),
    )

    msg = Mock()
    msg.headers = [("trace-id", b"error-trace")]
    msg.value = {"event": "ad.created", "payload": {"ad_id": 99}}

    initial_trace = "initial-trace"
    set_trace_id(initial_trace)

    try:
        await consumer._process_message(msg)
    except RuntimeError:
        pass

    assert get_trace_id() == initial_trace
