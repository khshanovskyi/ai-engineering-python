# HINTS — openai/responses

Detailed guidance for the TODOs in `client.py` (official SDK) and `custom_client.py` (raw HTTP)
for the **OpenAI Responses API** (`POST /v1/responses`). This is OpenAI's newer surface; the big
differences from Chat Completions:
- The system prompt goes in a dedicated **`instructions`** field (not a `system` *message*).
- The conversation turns go in **`input`** (here, just `[m.to_dict() for m in messages]`).
- The streaming SSE protocol uses **`event:` + `data:` line pairs** and typed events like
  `response.output_text.delta` (Chat Completions had only `data:`).

Implement the SDK client first, then mirror it with raw HTTP. Try the stub first; expand a section
when stuck.

<details>
<summary><code>client.py</code> — <code>OpenAIResponsesClient.__init__()</code> · wire up the SDK clients</summary>

Same pattern as Chat Completions: `super().__init__(base_url, model_name, system_prompt, api_key)`,
then `self._client = OpenAI(api_key=api_key, base_url=base_url)` and
`self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)`. Pass the **raw** key.
</details>

<details>
<summary><code>client.py</code> — <code>OpenAIResponsesClient.response()</code> · sync response (SDK)</summary>

**Steps:**
1. `input_messages = [message.to_dict() for message in messages]` (no system message inlined).
2. `response = self._client.responses.create(model=self._model_name, instructions=self._system_prompt, input=input_messages)`.
3. `content = response.output_text` — the SDK conveniently flattens all output text for you.
4. `print(content)`; return `Message(Role.ASSISTANT, content)`.
</details>

<details>
<summary><code>client.py</code> — <code>OpenAIResponsesClient.stream_response()</code> · streamed response (SDK)</summary>

**Steps:**
1. Same `input_messages`; `contents = []`.
2. Use the SDK's streaming context manager:
   `async with self._async_client.responses.stream(model=..., instructions=..., input=...) as stream:`.
3. `async for event in stream:` — events are typed. When `event.type == "response.output_text.delta"`,
   append `event.delta` and `print(event.delta, end='')`.
4. `print()` newline; return `Message(Role.ASSISTANT, "".join(contents))`.

**Key snippet:**
```python
async with self._async_client.responses.stream(
        model=self._model_name,
        instructions=self._system_prompt,
        input=input_messages,
) as stream:
    async for event in stream:
        if event.type == "response.output_text.delta":
            contents.append(event.delta)
            print(event.delta, end='')
```

**Gotcha:** the stream emits many event types (`response.created`, `...output_item.added`,
`...output_text.delta`, `...completed`, …). Only `response.output_text.delta` carries visible text.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomOpenAIResponsesClient.response()</code> · sync via raw HTTP</summary>

**Steps:**
1. `url = f"{self._base_url}/responses"`; headers `{"Authorization": self._api_key, "Content-Type": "application/json"}`
   (`self._api_key` already `"Bearer ..."`).
2. `request_data = {"model": ..., "instructions": self._system_prompt, "input": [m.to_dict() ...]}`.
3. `requests.post(...)`; on 200 parse with `_extract_output_text(data)`, print, return `Message`.
   On non-200 `raise Exception(f"HTTP {response.status_code}: {response.text}")`.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomOpenAIResponsesClient.stream_response()</code> · parse the event/data SSE stream</summary>

**What you're building:** hand-parse the Responses SSE stream, which interleaves `event:` and
`data:` lines.

**Steps:**
1. Same `url` / `headers`; `request_data` adds `"stream": True`.
2. `aiohttp` POST; if `status == 200`, keep an `event_type = None` and iterate the lines.
3. A line `"event: <name>"` → remember `event_type = name`.
4. A line `"data: {...}"` → **only parse it when** `event_type == "response.output_text.delta"`;
   then `json.loads`, take `delta`, print + append it.
5. A blank line `""` separates SSE events → reset `event_type = None`.
6. `print()` newline after the loop; return `Message(Role.ASSISTANT, "".join(contents))`.

**Key snippet (the event/data state machine):**
```python
event_type = None
async for line in response.content:
    line_str = line.decode('utf-8').strip()
    if line_str.startswith("event: "):
        event_type = line_str[7:].strip()
    elif line_str.startswith("data: ") and event_type == "response.output_text.delta":
        data = json.loads(line_str[6:])
        delta = data.get("delta", "")
        if delta:
            print(delta, end='')
            contents.append(delta)
    elif line_str == "":
        event_type = None
```

**Gotcha:** unlike Chat Completions, you **must** track the preceding `event:` line — a bare
`data:` payload is ambiguous on its own. There is no `[DONE]` sentinel to key off here; rely on
the event names instead.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomOpenAIResponsesClient._extract_output_text()</code> · walk the non-stream JSON (<code>@staticmethod</code>)</summary>

Walk the non-stream JSON to find the assistant text. The shape is
`{"output": [{"type": "message", "content": [{"type": "output_text", "text": "..."}]}]}`:
```python
output = data.get("output", [])
for item in output:
    if item.get("type") == "message":
        for content_part in item.get("content", []):
            if content_part.get("type") == "output_text":
                return content_part.get("text", "")
raise ValueError("No output text found in the response")
```

**Gotcha:** `output` can contain non-`message` items (e.g. reasoning); skip anything that isn't a
`message` with an `output_text` part.

**Docs:** https://platform.openai.com/docs/api-reference/responses
</details>
