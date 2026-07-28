import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

import aiohttp

log = logging.getLogger(__name__)

OLLAMA_ONLY_MODEL_PARAMS = frozenset({'num_ctx', 'num_predict'})

T = TypeVar('T')


def remove_ollama_only_model_params(params: dict) -> dict:
    for key in OLLAMA_ONLY_MODEL_PARAMS:
        params.pop(key, None)
    return params


def is_tool_continuation_payload(payload: dict) -> bool:
    messages = payload.get('messages', [])
    if isinstance(messages, list) and any(
        isinstance(message, dict) and message.get('role') == 'tool' for message in messages
    ):
        return True

    response_input = payload.get('input', [])
    return isinstance(response_input, list) and any(
        isinstance(item, dict) and item.get('type') == 'function_call_output' for item in response_input
    )


async def request_with_tool_continuation_retry(
    request_call: Callable[[], Awaitable[T]],
    *,
    is_tool_continuation: bool,
) -> T:
    attempts = 2 if is_tool_continuation else 1
    for attempt in range(attempts):
        try:
            return await request_call()
        except (TimeoutError, aiohttp.ClientConnectionError):
            if attempt + 1 >= attempts:
                raise
            log.warning('Tool-result continuation connection failed; retrying once')
            await asyncio.sleep(0.25)

    raise RuntimeError('Request retry loop completed without a result')
