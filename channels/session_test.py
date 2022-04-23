import inspect
import logging
from asyncio import CancelledError
from typing import Any, Awaitable, Callable, Dict, Optional

from rasa.core.channels.channel import (
    CollectingOutputChannel,
    InputChannel,
    UserMessage,
)
from sanic import response
from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse

logger = logging.getLogger(__name__)


class SessionTestInput(InputChannel):
    def name(self) -> str:
        return "session_test"

    def get_metadata(self, req: Request) -> Optional[Dict[str, Any]]:
        return req.json.get("metadata", {})

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender")
            text = request.json.get("text")
            input_channel = self.name()
            metadata = self.get_metadata(request)

            collector = CollectingOutputChannel()

            try:
                await on_new_message(
                    UserMessage(
                        text,
                        collector,
                        sender_id,
                        input_channel=input_channel,
                        metadata=metadata,
                    )
                )
            except CancelledError:
                logger.error(f"Message handling timed out for user message '{text}'.")
            except Exception:
                logger.exception(
                    f"An exception occured while handling user message '{text}'."
                )
            return response.json(collector.messages)

        return custom_webhook
