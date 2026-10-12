import logging
import typing

from aiokafka import AIOKafkaConsumer

from src.application.ports.usecases import IndexAdPort, RemoveAdPort
from src.infrastructure.tracing.context import reset_trace_id, set_trace_id

logger = logging.getLogger(__name__)


class KafkaAdsConsumer:
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        index_ad: IndexAdPort,
        remove_ad: RemoveAdPort,
    ) -> None:
        self._consumer = consumer
        self._index_ad = index_ad
        self._remove_ad = remove_ad

    async def run(self) -> None:
        async for msg in self._consumer:
            try:
                await self._process_message(msg)
            except Exception:
                logger.exception("failed to handle message %s", msg)
                continue
            await self._consumer.commit()

    async def _process_message(self, msg) -> None:
        """Lifecycle: extract header → set ContextVar → handle → reset."""
        token = None
        try:
            trace_id = self._extract_trace_id(msg.headers)
            if trace_id:
                token = set_trace_id(trace_id)
            await self._handle(msg.value)
        finally:
            if token:
                reset_trace_id(token)

    def _extract_trace_id(self, headers: list[tuple[str, bytes]] | None) -> str | None:
        if not headers:
            return None
        for key, value in headers:
            if key == "trace-id":
                return value.decode("utf-8")
        return None

    async def _handle(self, value: dict[str, typing.Any]) -> None:
        event = value.get("event")
        payload = value.get("payload") or {}
        ad_id = payload.get("ad_id")
        if not isinstance(ad_id, int):
            logger.warning("skip message without ad_id: %s", value)
            return

        if event in ("ad.created", "ad.updated"):
            await self._index_ad.execute(ad_id)
        elif event == "ad.deleted":
            await self._remove_ad.execute(ad_id)
        else:
            logger.warning("unknown event type: %s", event)
