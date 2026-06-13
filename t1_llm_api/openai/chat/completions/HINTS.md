# HINTS — openai/chat/completions

Detailed guidance for the TODOs in `client.py` (official SDK) and `custom_client.py` (raw HTTP).
Both talk to the **OpenAI Chat Completions API** (`POST /v1/chat/completions`) and produce the
same result — the custom client just shows what the SDK does under the hood. Implement the SDK
one first, then mirror it with raw HTTP. Try the stub first; expand a section when stuck.

**Shared request shape** (reused by every method below): a `system` message **inlined first**, then
every turn from history serialized with `Message.to_dict()` (`{"role": ..., "content": ...}`):
```python
messages_dicts = [
    {"role": "system", "content": self._system_prompt},
    *[message.to_dict() for message in messages],
]
```
Chat Completions takes the system prompt as a **message with role `system`** — unlike Anthropic /
Gemini / the Responses API, which use a dedicated field.

<details>
<summary><code>client.py</code> — <code>OpenAIChatCompletionsClient.__init__()</code> · wire up the SDK clients</summary>

**What you're building:** wire up the SDK clients on top of `BaseOpenAIClient`.

**Steps:**
1. `super().__init__(base_url, model_name, system_prompt, api_key)` (lets the base validate +
   Bearer-format the key).
2. Store `self._client = OpenAI(api_key=api_key, base_url=base_url)` and
   `self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)`.

**Gotcha:** pass the **raw** `api_key` here (the SDK adds `Bearer ` itself). `self._api_key` holds
the `"Bearer ..."` form, but that's for the *custom* client, not the SDK.
</details>

<details>
<summary><code>client.py</code> — <code>OpenAIChatCompletionsClient.response()</code> · sync chat completion (SDK)</summary>

**Steps:**
1. Build `messages_dicts` (system + history, see shared shape above).
2. `response = self._client.chat.completions.create(model=self._model_name, messages=messages_dicts)`.
3. Pull the text from `response.choices[0].message.content`.
4. `print(content)` and return `Message(role=Role.ASSISTANT, content=content)`.
</details>

<details>
<summary><code>client.py</code> — <code>OpenAIChatCompletionsClient.stream_response()</code> · streamed chat completion (SDK)</summary>

**Steps:**
1. Same `messages_dicts`; keep a `content = []` accumulator.
2. `stream = await self._async_client.chat.completions.create(model=..., stream=True, messages=...)`.
3. `async for chunk in stream:` read `chunk.choices[0].delta.content`; when it's truthy, append it
   and `print(delta_content, end='')`.
4. After the loop `print()` (newline) and return `Message(Role.ASSISTANT, "".join(content))`.

**Key snippet:**
```python
async for chunk in stream:
    if delta_content := chunk.choices[0].delta.content:   # delta.content is None on some chunks
        content.append(delta_content)
        print(delta_content, end='')
```

**Gotcha:** the first/last chunks may carry role or finish info with `delta.content == None`; the
walrus `if` guards against printing `None`.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomOpenAIChatCompletionsClient.response()</code> · sync via raw HTTP</summary>

**What you're building:** the same call with `requests`, no SDK.

**Steps:**
1. `url = f"{self._base_url}/chat/completions"` (base URL already ends in `/v1`).
2. Headers: `{"Authorization": self._api_key, "Content-Type": "application/json"}` — `self._api_key`
   is already `"Bearer ..."` thanks to `BaseOpenAIClient`.
3. Build `messages_dicts` (system + history) and `request_data = {"model": ..., "messages": ...}`.
4. `response = requests.post(url=url, headers=headers, json=request_data)`.
5. On `status_code == 200`: read `data["choices"][0]["message"]["content"]`, print it, return a
   `Message(Role.ASSISTANT, content)`. If `choices` is empty, `raise ValueError(...)`.
6. Otherwise `raise Exception(f"HTTP {response.status_code}: {response.text}")`.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomOpenAIChatCompletionsClient.stream_response()</code> · parse the SSE stream by hand</summary>

**What you're building:** parse the SSE stream by hand with `aiohttp`.

**Steps:**
1. Same `url` / `headers`; `request_data` adds `"stream": True`.
2. `async with aiohttp.ClientSession() as session:` then `async with session.post(...) as response:`.
3. If `response.status == 200`, iterate `async for line in response.content:`.
4. Decode + strip each line. SSE payload lines start with `"data: "`; slice off the 6-char prefix.
5. If the payload is `"[DONE]"`, the stream is finished — `print()` a newline. Otherwise pull the
   delta text via `_get_content_snippet(...)`, `print(..., end='')`, and append it.
6. On non-200, read `await response.text()` and surface the error.
7. Return `Message(Role.ASSISTANT, "".join(contents))`.

**Key snippet (the SSE loop):**
```python
async for line in response.content:
    line_str = line.decode('utf-8').strip()
    if line_str.startswith("data: "):
        data = line_str[6:].strip()
        if data != "[DONE]":
            content_snippet = self._get_content_snippet(data)
            print(content_snippet, end='')
            contents.append(content_snippet)
        else:
            print()
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomOpenAIChatCompletionsClient._get_content_snippet()</code> · pull delta text from one SSE chunk</summary>

Parse one SSE `data:` JSON chunk into its delta text:
```python
data = json.loads(data)
if choices := data.get("choices"):
    delta = choices[0].get("delta", {})
    return delta.get("content", '')
return ''
```

**Gotchas:**
- Each `data:` line is a standalone JSON object shaped like the non-stream response but with a
  `delta` instead of a `message`. Use `.get(...)` defensively — some chunks have an empty `delta`.
- Chat Completions streams use **only `data:` lines** (plus the `[DONE]` sentinel). This differs
  from the Responses API, which also emits `event:` lines — see `responses/HINTS.md`.

**Docs:** https://platform.openai.com/docs/api-reference/chat/create
</details>
