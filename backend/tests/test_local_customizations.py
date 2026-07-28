import asyncio

import aiohttp
import pytest
from open_webui.utils.fact_check import (
    dedupe_queries,
    is_explicit_web_search_request,
    looks_like_fact_check_request,
    trim_web_search_results,
)
from open_webui.utils.mcp.naming import allocate_mcp_tool_name
from open_webui.utils.payload import (
    apply_model_params_to_body_ollama,
    apply_model_params_to_body_openai,
)
from open_webui.utils.provider_compat import (
    is_tool_continuation_payload,
    request_with_tool_continuation_retry,
)


@pytest.mark.parametrize(
    ('payload', 'expected'),
    [
        ({'messages': [{'role': 'tool', 'content': 'done'}]}, True),
        ({'input': [{'type': 'function_call_output', 'output': 'done'}]}, True),
        ({'messages': [{'role': 'user', 'content': 'hello'}]}, False),
        ({'input': 'not-a-list'}, False),
    ],
)
def test_tool_continuation_detection(payload, expected):
    assert is_tool_continuation_payload(payload) is expected


@pytest.mark.asyncio
async def test_tool_continuation_retries_connection_failure_once(monkeypatch):
    attempts = 0

    async def request_call():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise aiohttp.ClientConnectionError('reset')
        return 'response'

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr(asyncio, 'sleep', no_sleep)

    assert await request_with_tool_continuation_retry(request_call, is_tool_continuation=True) == 'response'
    assert attempts == 2


@pytest.mark.asyncio
async def test_initial_request_does_not_retry():
    attempts = 0

    async def request_call():
        nonlocal attempts
        attempts += 1
        raise TimeoutError

    with pytest.raises(asyncio.TimeoutError):
        await request_with_tool_continuation_retry(request_call, is_tool_continuation=False)
    assert attempts == 1


def test_openai_params_filter_ollama_only_defaults_but_allow_custom_override():
    params = {
        'temperature': '0.5',
        'num_ctx': 8192,
        'num_predict': 512,
        'custom_params': {'num_ctx': 32768},
    }

    result = apply_model_params_to_body_openai(params, {'model': 'compatible-model'})

    assert result['temperature'] == 0.5
    assert result['num_ctx'] == 32768
    assert 'num_predict' not in result


def test_ollama_params_remain_in_options():
    result = apply_model_params_to_body_ollama(
        {'num_ctx': 8192, 'num_predict': 512},
        {'model': 'ollama-model'},
    )

    assert result['options']['num_ctx'] == 8192
    assert result['options']['num_predict'] == 512


def test_mcp_tool_name_prefers_remote_name_and_resolves_collisions():
    assert allocate_mcp_tool_name('search_web', 'mcp4chatgpt-local', {}) == 'search_web'
    assert (
        allocate_mcp_tool_name(
            'search_web',
            'mcp4chatgpt-local',
            {'search_web', 'mcp4chatgpt_local_search_web'},
        )
        == 'mcp4chatgpt_local_search_web_2'
    )


def test_fact_check_and_explicit_search_intent():
    assert looks_like_fact_check_request('请核查附件中的历史说法')
    assert looks_like_fact_check_request('Fact-check the attached transcript')
    assert is_explicit_web_search_request('请联网搜索并查证')
    assert not is_explicit_web_search_request('总结这个附件')


def test_query_deduplication_and_result_trimming():
    assert dedupe_queries([' Alpha ', 'alpha', '', 'Beta', 'Gamma'], limit=2) == ['Alpha', 'Beta']

    original = {
        'filenames': [f'url-{index}' for index in range(10)],
        'items': list(range(10)),
        'docs': list(range(10)),
        'collection_names': ['collection'],
    }
    trimmed = trim_web_search_results(original, limit=3)

    assert trimmed['filenames'] == ['url-0', 'url-1', 'url-2']
    assert trimmed['items'] == [0, 1, 2]
    assert trimmed['docs'] == [0, 1, 2]
    assert original['filenames'] == [f'url-{index}' for index in range(10)]
