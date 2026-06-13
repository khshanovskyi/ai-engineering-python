# HINTS — gemini/interactions

Detailed guidance for the TODOs in `client.py` (official `google-genai` SDK) and
`custom_client.py` (raw HTTP) for Gemini's **Interactions API** (`POST /v1beta/interactions`).
Implement the SDK client first, then mirror it with raw HTTP. Try the stub first; expand a section
when stuck.

Both clients extend `BaseGeminiClient` (`gemini/base.py`), which already gives you:
- `_auth_headers()` → `{"Content-Type": "application/json", "x-goog-api-key": self._api_key}`
  (Gemini authenticates with the **`x-goog-api-key`** header, not `Authorization`).
- `_to_gemini_role(role)` → `"model"` for assistant, else `"user"` (the classic Gemini quirk:
  the assistant role is called **`model`**). The Interactions API expresses this through step
  *types* instead — see `_to_input` below.

What's different about the Interactions API: instead of a flat `messages` list it takes an
**`input`** list of typed *steps*, the system prompt goes in **`system_instruction`**, and
generation settings live under **`generation_config`** (e.g. `max_output_tokens`).

<details>
<summary><code>client.py</code> — <code>GeminiInteractionsAIClient.__init__()</code> · wire up the google-genai SDK client</summary>

**Steps:**
1. `super().__init__(base_url, model_name, api_key, system_prompt)`.
2. Build the SDK client, pointing it at our `base_url` via `HttpOptions`:
   ```python
   self._client = genai.Client(api_key=api_key, http_options=types.HttpOptions(base_url=base_url))
   ```
</details>

<details>
<summary><code>client.py</code> — <code>GeminiInteractionsAIClient._to_input()</code> · map messages to Interactions steps</summary>

Convert our `Message` list into Interactions *steps*. Assistant turns become `model_output`,
everything else `user_input`; the text is wrapped in a content block list:
```python
steps = []
for msg in messages:
    step_type = "model_output" if msg.role == Role.ASSISTANT else "user_input"
    steps.append({"type": step_type, "content": [{"type": "text", "text": msg.content}]})
return steps
```
</details>

<details>
<summary><code>client.py</code> — <code>GeminiInteractionsAIClient.response()</code> · sync interaction (SDK)</summary>

**Steps:**
1. `interaction = self._client.interactions.create(model=self._model_name, input=self._to_input(messages), system_instruction=self._system_prompt, generation_config={"max_output_tokens": kwargs.get("max_tokens", 1024)})`.
2. `content = interaction.output_text`; `print(content)`; return `Message(Role.ASSISTANT, content)`.
</details>

<details>
<summary><code>client.py</code> — <code>GeminiInteractionsAIClient.stream_response()</code> · streamed interaction (SDK)</summary>

**Steps:**
1. Use the async namespace with `stream=True`:
   `stream = await self._client.aio.interactions.create(..., stream=True)`.
2. `async for event in stream:` — visible text arrives when
   `event.event_type == "step.delta"` **and** `event.delta.type == "text"`; append + print
   `event.delta.text`.
3. `print()` newline; return `Message(Role.ASSISTANT, "".join(content))`.

**Key snippet:**
```python
async for event in stream:
    if event.event_type == "step.delta" and event.delta.type == "text":
        content.append(event.delta.text)
        print(event.delta.text, end='')
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiInteractionsAIClient._to_input()</code> · map messages to Interactions steps</summary>

Identical to the SDK client's `_to_input` (same step mapping):
```python
steps = []
for msg in messages:
    step_type = "model_output" if msg.role == Role.ASSISTANT else "user_input"
    steps.append({"type": step_type, "content": [{"type": "text", "text": msg.content}]})
return steps
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiInteractionsAIClient._headers()</code> · auth headers + API revision</summary>

Extend the base auth headers with the API revision pin:
```python
return {**self._auth_headers(), "Api-Revision": GEMINI_API_REVISION}   # from commons.constants
```
`_auth_headers()` (from `BaseGeminiClient`) already sets `Content-Type` and `x-goog-api-key`.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiInteractionsAIClient._request_body()</code> · build the JSON payload</summary>

Build the JSON payload, adding `stream` only when streaming:
```python
body = {
    "model": self._model_name,
    "input": self._to_input(messages),
    "system_instruction": self._system_prompt,
    "generation_config": {"max_output_tokens": kwargs.get("max_tokens", 1024)},
}
if stream:
    body["stream"] = True
return body
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiInteractionsAIClient._extract_text()</code> · walk the non-stream JSON (<code>@staticmethod</code>)</summary>

Collect `text` blocks from every `model_output` step:
```python
texts = []
for step in interaction.get("steps", []):
    if step.get("type") == "model_output":
        for block in step.get("content", []):
            if block.get("type") == "text":
                texts.append(block.get("text", ""))
return "".join(texts)
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiInteractionsAIClient.response()</code> · sync via raw HTTP</summary>

**Steps:**
1. `url = f"{self._base_url}/v1beta/interactions"` (`GEMINI_BASE_URL` is the bare host).
2. `requests.post(url=url, headers=self._headers(), json=self._request_body(messages, stream=False, **kwargs))`.
3. On 200 → `_extract_text(response.json())`, print, return `Message`. On non-200 → `raise Exception(...)`.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiInteractionsAIClient.stream_response()</code> · parse the Gemini SSE stream</summary>

**What you're building:** hand-parse the Gemini SSE stream.

**Steps:**
1. `url = f"{self._base_url}/v1beta/interactions?alt=sse"` — **streaming requires `?alt=sse`**;
   without it Gemini returns a single JSON blob instead of an event stream.
2. `aiohttp` POST with `_headers()` and `_request_body(..., stream=True, ...)`.
3. Iterate lines; payload lines start with `"data: "`. Slice the prefix; skip empty payloads and a
   `"[DONE]"` sentinel (`continue`).
4. `json.loads` the rest; when `event_type == "step.delta"` and `delta["type"] == "text"`, print +
   append `delta["text"]`.
5. `print()` newline; return `Message(Role.ASSISTANT, "".join(contents))`.

**Key snippet (the SSE loop):**
```python
async for line in response.content:
    line_str = line.decode('utf-8').strip()
    if line_str.startswith("data: "):
        data = line_str[6:].strip()
        if not data or data == "[DONE]":
            continue
        event = json.loads(data)
        if event.get("event_type") == "step.delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text":
                text = delta.get("text", "")
                if text:
                    print(text, end='')
                    contents.append(text)
```

**Gotchas:**
- The SDK's `event.event_type` / `event.delta.type` map directly onto the raw JSON keys
  `"event_type"` / `delta["type"]` — that's the SDK↔HTTP correspondence to notice.
- Don't forget `?alt=sse`; it's the single most common reason a Gemini stream "doesn't stream."

**Docs:** https://ai.google.dev/gemini-api/docs
</details>
