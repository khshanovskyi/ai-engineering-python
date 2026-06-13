# HINTS — anthropic

Detailed guidance for the TODOs in `client.py` (official SDK) and `custom_client.py` (raw HTTP)
for the **Anthropic Messages API** (`POST /v1/messages`). Implement the SDK client first, then
mirror it with raw HTTP. Try the stub first; expand a section when stuck.

What's different from OpenAI:
- The system prompt is a **dedicated `system` parameter**, not a message in the list.
- **`max_tokens` is required** on every request (OpenAI defaults it; Anthropic rejects requests
  without it). Use `kwargs.get("max_tokens", 1024)`.
- Auth uses **`x-api-key`** + a required **`anthropic-version`** header — *not* `Authorization: Bearer`.
- Responses are an **array of content blocks**; concatenate the `text` blocks.
- `AnthropicAIClient` extends `AIClient` directly (there is no `BaseOpenAIClient`-style base here),
  so `self._api_key` is the **raw** key — exactly what both the SDK and the `x-api-key` header want.

<details>
<summary><code>client.py</code> — <code>AnthropicAIClient.__init__()</code> · wire up the SDK clients</summary>

**Steps:**
1. `super().__init__(base_url, model_name, api_key, system_prompt)` — note `AIClient`'s order is
   `(base_url, model_name, api_key, system_prompt)`.
2. `self._client = Anthropic(api_key=api_key, base_url=base_url)` and
   `self._async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)`.
</details>

<details>
<summary><code>client.py</code> — <code>AnthropicAIClient.response()</code> · sync message (SDK)</summary>

**Steps:**
1. `response = self._client.messages.create(system=self._system_prompt, max_tokens=1024, model=self._model_name, messages=[m.to_dict() for m in messages])`.
2. The reply is `response.content`, a list of blocks. Concatenate the text of `block.type == 'text'` blocks.
3. `print(content)`; return `Message(Role.ASSISTANT, content)`.

**Key snippet:**
```python
content = ""
for block in response.content:
    if block.type == 'text':
        content += block.text
```
</details>

<details>
<summary><code>client.py</code> — <code>AnthropicAIClient.stream_response()</code> · streamed message (SDK)</summary>

**Steps:**
1. `stream = await self._async_client.messages.create(system=..., max_tokens=1024, model=..., stream=True, messages=...)`.
2. `async for chunk in stream:` — Anthropic emits typed events. Text arrives on
   `chunk.type == "content_block_delta"` as `chunk.delta.text`. Guard with `hasattr` since other
   event types (`message_start`, `content_block_start`, `message_delta`, …) lack `.delta.text`.
3. Append + `print(..., end='')` each delta; `print()` newline at the end; return the `Message`.

**Key snippet:**
```python
async for chunk in stream:
    if chunk.type == "content_block_delta":
        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
            content.append(chunk.delta.text)
            print(chunk.delta.text, end='')
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomAnthropicAIClient.response()</code> · sync via raw HTTP</summary>

**Steps:**
1. `url = f"{self._base_url}/v1/messages"` — `ANTHROPIC_BASE_URL` is the **bare host** (no `/v1`),
   so you append `/v1/messages` yourself. (Contrast OpenAI, whose base URL already ends in `/v1`.)
2. Headers:
   ```python
   {"x-api-key": self._api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
   ```
   `self._api_key` is the raw key — Anthropic does **not** use `Authorization: Bearer`.
3. `request_data = {"model": ..., "system": self._system_prompt, "max_tokens": kwargs.get("max_tokens", 1024), "messages": [m.to_dict() ...]}`.
4. `requests.post(...)`; on 200 read `data["content"]` (list of blocks), join the `text` of
   `type == "text"` blocks, print, return `Message`. If the list is empty, `raise ValueError(...)`.
   On non-200 `raise Exception(f"HTTP {response.status_code}: {response.text}")`.

**Key snippet:**
```python
content_blocks = data.get("content", [])
content = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomAnthropicAIClient.stream_response()</code> · parse Anthropic's SSE stream</summary>

**What you're building:** parse Anthropic's SSE stream by hand.

**Steps:**
1. Same `url` / `headers`; `request_data` adds `"stream": True`.
2. `aiohttp` POST; if `status == 200` iterate `async for line in response.content:`.
3. Each payload line starts with `"data: "`. Slice the prefix and `json.loads` it. (Anthropic also
   emits `event:` lines, but the `data:` JSON carries its own `"type"`, so keying off the parsed
   `type` is enough — no need to track the `event:` line like the OpenAI Responses client.)
4. On `type == "content_block_delta"` with `delta["type"] == "text_delta"`, print + append
   `delta["text"]`. On `type == "message_stop"`, `break`.
5. `print()` newline; return `Message(Role.ASSISTANT, "".join(contents))`.

**Key snippet (the SSE loop):**
```python
async for line in response.content:
    line_str = line.decode('utf-8').strip()
    if line_str.startswith("data: "):
        parsed = json.loads(line_str[6:].strip())
        event_type = parsed.get("type")
        if event_type == "content_block_delta":
            delta = parsed.get("delta", {})
            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                if text:
                    print(text, end='')
                    contents.append(text)
        elif event_type == "message_stop":
            break
```

**Gotcha:** Anthropic's event sequence is `message_start` → `content_block_start` →
`content_block_delta`* → `content_block_stop` → `message_delta` → `message_stop`. Only
`content_block_delta` + `text_delta` is visible text; everything else is metadata.

**Docs:** https://docs.claude.com/en/api/messages
</details>
