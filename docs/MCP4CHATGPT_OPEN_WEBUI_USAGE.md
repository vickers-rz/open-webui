# MCP4ChatGPT 在 Open WebUI 对话页中的使用说明

本文说明如何在 Open WebUI 前端对话页面启用 MCP4ChatGPT，让模型通过 MCP 工具自然地搜索和分析网上内容。

## 适用边界

这里使用的是 Open WebUI 的对话工具系统，不是 Open WebUI 内置的 Web Search。

不需要修改：

- `Admin Panel -> Settings -> Web Search`
- `External Search URL`
- `Web Search Engine`
- `Bypass Web Search Web Loader`

MCP4ChatGPT 服务地址：

```text
http://127.0.0.1:8766/mcp
```

当前本机 MCP server id：

```text
mcp4chatgpt_local
```

## 启用方式

1. 在 Open WebUI 新建对话。
2. 点击输入框附近的 `Available Tools`、`工具` 或 `扩展功能`。
3. 启用 `MCP4ChatGPT Local Full Tools`。
4. 不要开启 Open WebUI 的内置联网搜索按钮。
5. 直接用自然语言提出联网搜索请求。

例如：

```text
请搜索 Open WebUI 关于 Agentic Search 的官方文档，
比较 Native Mode 与 Traditional RAG，并附来源链接。
```

模型应自动调用：

```text
search_web
```

不需要在提示词中写 MCP server id、函数全名或 JSON 参数。

## 搜索工具

MCP4ChatGPT 对模型只公开一个日常搜索入口：

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
- `deep_read`：是否进一步抓取前两个结果的网页正文，默认关闭。

内部行为：

```text
优先使用 Brave 搜索
-> Brave 失败或没有结果时回退 Firecrawl
-> deep_read=true 时使用 Firecrawl 抓取最多两个网页正文
-> 返回标题、链接和摘要或正文
```

普通搜索建议保持 `deep_read=false`。只有在比较文档、分析长文或用户明确要求依据网页正文时，才使用 `deep_read=true`。

## 工具命名规则

Open WebUI 对 MCP 工具采用“原名优先、冲突时增加前缀”的规则。

没有其他已启用工具也叫 `search_web` 时，模型看到并调用：

```text
search_web
```

如果多个已启用工具服务器都提供同名工具，Open WebUI 会为发生冲突的工具生成带服务器 id 的名称，例如：

```text
mcp4chatgpt_local_search_web
```

工具展示名称、发送给模型的函数名和执行器注册名始终保持一致。

## 推荐用法

普通联网查询：

```text
请搜索西安未来几天的天气预报，按日期列出天气、最高温和最低温，并附来源。
```

比较多个来源：

```text
请搜索三个可靠来源，比较 Brave Search 与 Firecrawl 的适用场景，并给出引用。
```

要求读取网页正文：

```text
请搜索 Open WebUI Agentic Search 的官方文档，并深入阅读最相关页面，
比较 Native Mode 与 Traditional RAG。答案必须依据网页正文并附来源。
```

模型在最后一种场景中应调用：

```json
{
  "query": "Open WebUI Agentic Search Native Mode Traditional RAG",
  "result_count": 3,
  "deep_read": true
}
```

## 搜索后写入 Sublime Text

MCP4ChatGPT 同时包含网页搜索和 co-te 本机应用能力。只启用 `MCP4ChatGPT Local Full Tools` 后，可以直接提交跨能力任务：

```text
请在网上搜索关于大模型应用开发所需要的技术栈，
分别从中国、美国、欧洲和东南亚就业市场分析岗位需求、主流技术和学习优先级。
整理成带来源链接的中文 Markdown 报告，然后实际写入 Sublime Text。
写入后回读 Sublime Text，确认四个地区章节都存在。
```

预期工具流程：

```text
search_web
-> 整理 Markdown 报告
-> app_write_text(app=sublime_text, mode=replace_all)
-> app_get_context(app=sublime_text)
```

复杂跨地区任务可能触发多次 `search_web`。如果模型生成报告后只说“将写入”但没有调用写入工具，可以在同一对话中继续要求：

```text
不要再次搜索或复述报告。请立即调用 app_write_text 把上面的完整报告写入 Sublime Text，
随后调用 app_get_context 回读确认。
```

## 兼容性

以下旧工具名仍可通过 MCP `tools/call` 直接调用，但不会再出现在 `tools/list` 中，也不会提供给模型选择：

```text
web_search
web_brave_search
web_search_auto
web_combined_search
```

这样可以兼容已有脚本，同时避免模型在多个功能重叠的搜索工具之间选错。

网页抓取、站点遍历等用途不同的高级工具仍正常公开：

```text
web_scrape
web_crawl
web_map
web_extract
web_interact
```

## 故障判断

### 页面显示工具结果但没有最终回答

这表示搜索工具可能已经成功，失败发生在模型读取工具结果并继续生成答案的阶段。

Open WebUI 会在工具结果续写请求遇到连接重置或超时时自动重试一次。重试只复用已有工具结果，不会再次调用 Brave 或 Firecrawl。

如果重试后仍失败：

1. 点击重新生成。
2. 暂时保持 `deep_read=false`。
3. 检查模型提供商连接状态。

### 模型没有调用工具

确认输入框附近已启用 `MCP4ChatGPT Local Full Tools`，并在请求中明确使用“搜索”“联网查询”“查找最新资料”等表达。

### 工具名称带上服务器前缀

这表示当前对话同时启用了另一个同名工具。关闭冲突的工具服务器，或明确指定界面显示的带前缀名称。

## 成功标准

一次完整调用应依次出现：

```text
自然语言问题
-> search_web 工具调用
-> 搜索结果
-> 模型生成带来源链接的最终回答
```

验证时应同时确认：

- 没有开启 Open WebUI 内置 Web Search。
- 工具调用名称为 `search_web`，无重名时不带前缀。
- 回答包含真实网页标题或来源链接。
- 普通搜索使用摘要，深度分析才抓取正文。
