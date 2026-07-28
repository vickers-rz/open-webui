import re
from collections.abc import Collection


def allocate_mcp_tool_name(remote_name: str, server_id: str, used_names: Collection[str]) -> str:
    if remote_name not in used_names:
        return remote_name

    server_prefix = re.sub(r'[^A-Za-z0-9_]+', '_', server_id).strip('_') or 'mcp'
    base_name = f'{server_prefix}_{remote_name}'
    candidate = base_name
    suffix = 2

    while candidate in used_names:
        candidate = f'{base_name}_{suffix}'
        suffix += 1

    return candidate
