import re

FACT_CHECK_INTENT_RE = re.compile(
    r'(核查|查证|事实|属实|真实性|客观|fact[- ]?check|verify|verification)',
    re.IGNORECASE,
)

EXPLICIT_WEB_SEARCH_MARKERS = (
    '联网',
    '搜索',
    '搜搜',
    '核查',
    '查证',
    '查找',
    '检索',
    'fact check',
    'fact-check',
    'web search',
    'search web',
    'internet',
    'online',
)


def looks_like_fact_check_request(prompt: str | None) -> bool:
    return bool(prompt and FACT_CHECK_INTENT_RE.search(prompt))


def is_explicit_web_search_request(prompt: str | None) -> bool:
    normalized_prompt = (prompt or '').lower()
    return any(marker in normalized_prompt for marker in EXPLICIT_WEB_SEARCH_MARKERS)


def dedupe_queries(queries: list[str], limit: int = 3) -> list[str]:
    deduped = []
    seen = set()
    for query in queries:
        query = re.sub(r'\s+', ' ', str(query or '')).strip()
        if not query:
            continue
        key = query.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(query)
        if len(deduped) >= limit:
            break
    return deduped


def trim_web_search_results(results: dict, limit: int = 8) -> dict:
    if not isinstance(results, dict):
        return results

    trimmed = dict(results)
    for key in ('filenames', 'items', 'docs'):
        if isinstance(trimmed.get(key), list):
            trimmed[key] = trimmed[key][:limit]
    return trimmed
