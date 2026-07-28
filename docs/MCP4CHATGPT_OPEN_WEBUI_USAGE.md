# MCP4ChatGPT 在 Open WebUI v0.11.0 中的使用说明

本文说明如何在 Open WebUI 对话页面启用 MCP4ChatGPT，让模型通过 MCP 工具搜索和分析网上内容。

## 适用边界

这里使用的是 Open WebUI 的 MCP 工具系统，不是管理面板中的内置 Web Search。无需修改 Web Search Engine、External Search URL 或 Web Loader 设置。

默认本机服务地址：

```text
http://127.0.0.1:8766/mcp
```

示例 MCP server id：

```text
mcp4chatgpt_local
```

## 启用方式

1. 在 Open WebUI v0.11.0 新建或打开对话。
2. 从输入框的工具菜单启用 `MCP4ChatGPT Local Full Tools`。
3. 不要同时开启功能重叠的内置 Web Search。
4. 直接用自然语言提出联网搜索请求。

例如：

```text
请搜索 Open WebUI 关于 Agentic Search 的官方文档，
比较 Native Mode 与 Traditional RAG，并附来源链接。
```

模型应自动调用 `search_web`，无需在提示词中写服务器 id、完整函数名或 JSON 参数。

## 搜索工具

日常搜索入口：

```text
search_web
```

参数：

```json
{
  "query": "要搜索的问题",
  "result_count": 3,
  "deep_read": false
}
```

- `query`：搜索问题，必填。
- `result_count`：返回结果数量，默认 3，范围 1 至 10。
- `deep_read`：是否进一步读取最相关网页的正文。

普通搜索建议保持 `deep_read=false`。比较文档、分析长文或用户明确要求依据正文时，再使用 `deep_read=true`。

## 工具命名规则

Open WebUI 使用“原名优先、冲突时增加前缀”的规则。

没有其他工具占用名称时，模型看到：

```text
search_web
```

发生重名时，后注册的 MCP 工具会获得服务器前缀：

```text
mcp4chatgpt_local_search_web
```

如果前缀名称仍冲突，则依次追加 `_2`、`_3`。展示名称、发送给模型的函数名和执行器注册名保持一致。

## 推荐用法

普通查询：

```text
请搜索西安未来几天的天气预报，按日期列出天气、最高温和最低温，并附来源。
```

深入阅读：

```text
请搜索 Open WebUI Agentic Search 的官方文档并深入阅读最相关页面，
比较 Native Mode 与 Traditional RAG，答案必须依据正文并附来源。
```

附件事实核查使用 Open WebUI 内置 Web Search，而不是 MCP 搜索工具。附加文档后开启 Web Search，并明确使用“核查”“查证”“fact-check”或“verify”等表达。系统会从附件提取可验证主张、生成搜索词并按主张给出核查结果。只要求总结附件时，不会自动联网。

## 跨工具任务

启用包含搜索与本机应用能力的完整 MCP 工具集后，可以直接提交跨能力任务：

```text
请搜索大模型应用开发所需的技术栈，整理成带来源链接的中文 Markdown 报告，
然后写入 Sublime Text，并回读确认主要章节都存在。
```

预期流程：

```text
search_web
-> 整理 Markdown
-> app_write_text
-> app_get_context
```

## 故障判断

### 工具返回结果但没有最终回答

失败通常发生在模型读取工具结果并继续生成答案的阶段。Open WebUI 会在续接请求遇到连接重置或超时时自动重试一次；已有工具结果会被复用，不会重新执行 MCP 工具。

重试后仍失败时：

1. 点击重新生成。
2. 暂时使用 `deep_read=false`。
3. 检查模型提供商连接状态。

### 模型没有调用工具

确认当前对话已启用 `MCP4ChatGPT Local Full Tools`，并在请求中明确使用“搜索”“联网查询”或“查找最新资料”等表达。

### 工具名称带服务器前缀

这表示当前对话还有其他同名工具。关闭冲突的工具服务器，或使用界面显示的带前缀名称。

## 成功标准

一次完整调用应依次出现：

```text
自然语言问题
-> search_web 工具调用
-> 搜索结果
-> 模型生成带来源链接的最终回答
```

同时确认：

- 没有开启功能重叠的内置 Web Search。
- 无重名时工具调用名称为 `search_web`。
- 回答包含真实网页标题或来源链接。
- 普通搜索使用摘要，深度分析才读取正文。
