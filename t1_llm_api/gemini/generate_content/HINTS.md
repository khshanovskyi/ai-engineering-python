# HINTS — gemini/generate_content

Detailed guidance for the TODOs in `client.py` (official `google-genai` SDK) and
`custom_client.py` (raw HTTP) for Gemini's classic **Generate Content API**
(`POST /v1beta/models/{model}:generateContent`, and `:streamGenerateContent?alt=sse` for
streaming). Implement the SDK client first, then mirror it with raw HTTP. Try the stub first;
expand a section when stuck.

This is the *other* Gemini surface — compare with `gemini/interactions/HINTS.md`, which uses the
newer Interactions API (typed `input` steps). Here the shapes are different:
- History goes in **`contents`**, a list of `{"role": ..., "parts": [{"text": ...}]}` objects
  (SDK: `types.Content(role=..., parts=[types.Part(text=...)])`).
- The system prompt is **`system_instruction`** and generation settings live under
  **`generationConfig`** (REST, camelCase) / `GenerateContentConfig` (SDK).
- The reply comes back as **`candidates[0].content.parts[*].text`** (SDK exposes `response.text`).

Both clients extend `BaseGeminiClient` (`gemini/base.py`), which already gives you:
- `_to_gemini_role(role)` → `"model"` for `Role.ASSISTANT`, else `"user"` — the classic Gemini
  quirk: the assistant role is called **`model`**. Use it when building `contents`.
- `_auth_headers()` → `{"Content-Type": "application/json", "x-goog-api-key": self._api_key}`
  (Gemini authenticates with the **`x-goog-api-key`** header, not `Authorization`). The custom
  client uses this directly — no extra `Api-Revision` header is needed for this API.

<details>
<summary><code>client.py</code> — <code>GeminiGenerateContentAIClient.__init__()</code> · wire up the google-genai SDK client</summary>

**Steps:**
1. `super().__init__(base_url, model_name, api_key, system_prompt)`.
2. Build the SDK client, pointing it at our `base_url` via `HttpOptions`:
   ```python
   self._client = genai.Client(api_key=api_key, http_options=types.HttpOptions(base_url=base_url))
   ```
</details>

<details>
<summary><code>client.py</code> — <code>GeminiGenerateContentAIClient._to_gemini_contents()</code> · map messages to <code>types.Content</code></summary>

Convert each `Message` into a typed `types.Content`, mapping the role with `_to_gemini_role` and
wrapping the text in a single `types.Part`:
```python
contents = []
for msg in messages:
    contents.append(
        types.Content(
            role=self._to_gemini_role(msg.role),          # assistant -> "model"
            parts=[types.Part(text=msg.content)],
        )
    )
return contents
```
</details>

<details>
<summary><code>client.py</code> — <code>GeminiGenerateContentAIClient.response()</code> · sync generateContent (SDK)</summary>

**Steps:**
1. `response = self._client.models.generate_content(model=self._model_name, contents=self._to_gemini_contents(messages), config=types.GenerateContentConfig(system_instruction=self._system_prompt, max_output_tokens=kwargs.get("max_tokens", 1024)))`.
2. `content = response.text` — the SDK flattens the candidate parts for you.
3. `print(content)`; return `Message(Role.ASSISTANT, content)`.

**Gotcha:** the system prompt and `max_output_tokens` go **inside** `config=GenerateContentConfig(...)`,
not as top-level keyword args.
</details>

<details>
<summary><code>client.py</code> — <code>GeminiGenerateContentAIClient.stream_response()</code> · streamed generateContent (SDK)</summary>

**Steps:**
1. Call the async streaming helper and **`await` it first, then `async for`** over the result:
   `async for chunk in await self._client.aio.models.generate_content_stream(...)`.
2. Pass the same `model`, `contents`, and `config=types.GenerateContentConfig(...)`.
3. When `chunk.text` is truthy, append it and `print(chunk.text, end='')`.
4. `print()` newline; return `Message(Role.ASSISTANT, "".join(content))`.

**Key snippet:**
```python
async for chunk in await self._client.aio.models.generate_content_stream(
        model=self._model_name,
        contents=self._to_gemini_contents(messages),
        config=types.GenerateContentConfig(
            system_instruction=self._system_prompt,
            max_output_tokens=kwargs.get("max_tokens", 1024),
        ),
):
    if chunk.text:
        content.append(chunk.text)
        print(chunk.text, end='')
```

**Gotcha:** `generate_content_stream` returns a coroutine that resolves to an async iterator — note
the `async for ... in await ...` double step.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiGenerateContentAIClient._to_gemini_contents()</code> · map messages to content dicts</summary>

Same mapping as the SDK client, but plain dicts instead of `types.Content`:
```python
contents = []
for msg in messages:
    contents.append({
        "role": self._to_gemini_role(msg.role),   # assistant -> "model"
        "parts": [{"text": msg.content}],
    })
return contents
```
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiGenerateContentAIClient.response()</code> · sync via raw HTTP</summary>

**Steps:**
1. `url = f"{self._base_url}/v1beta/models/{self._model_name}:generateContent"` — `GEMINI_BASE_URL`
   is the bare host, and the model name is part of the **path** (`:generateContent` suffix).
2. `headers = self._auth_headers()` (sets `x-goog-api-key`).
3. Build the request body — note the REST shapes:
   ```python
   request_data = {
       "system_instruction": {"parts": [{"text": self._system_prompt}]},
       "contents": self._to_gemini_contents(messages),
       "generationConfig": {"maxOutputTokens": kwargs.get("max_tokens", 1024)},
   }
   ```
4. `requests.post(...)`; on 200, read `candidates[0]["content"]["parts"]` and join each part's
   `text`, print, return `Message(Role.ASSISTANT, content)`. If there are no candidates,
   `raise ValueError(...)`. On non-200, `raise Exception(f"HTTP {response.status_code}: {response.text}")`.

**Gotchas:**
- `system_instruction` is an **object with `parts`** here (`{"parts": [{"text": ...}]}`), not a bare
  string — different from OpenAI's `instructions` and Anthropic's `system`.
- REST uses **camelCase** (`generationConfig`, `maxOutputTokens`) while the SDK uses snake_case
  (`max_output_tokens`). Easy to get wrong when porting between the two clients.
</details>

<details>
<summary><code>custom_client.py</code> — <code>CustomGeminiGenerateContentAIClient.stream_response()</code> · parse the SSE stream</summary>

**What you're building:** hand-parse the streaming Generate Content SSE response.

**Steps:**
1. `url = f"{self._base_url}/v1beta/models/{self._model_name}:streamGenerateContent?alt=sse"` —
   note the `:streamGenerateContent` method **and** the required **`?alt=sse`** (without it Gemini
   returns one JSON array instead of an event stream).
2. Same `headers` and `request_data` as the sync call.
3. `aiohttp` POST; if `status == 200`, iterate lines. Each payload line starts with `"data: "`;
   strip the prefix and `json.loads` it.
4. For each parsed chunk, walk `candidates[0]["content"]["parts"]` and print + append every part's
   `text`. (There's no `event:` line and no `[DONE]` sentinel to handle for this API.)
5. On non-200, read + print the error. `print()` newline; return `Message(Role.ASSISTANT, "".join(contents))`.

**Key snippet (the SSE loop):**
```python
async for line in response.content:
    line_str = line.decode('utf-8').strip()
    if line_str.startswith("data: "):
        parsed_data = json.loads(line_str[6:].strip())
        candidates = parsed_data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                text_content = part.get("text", "")
                if text_content:
                    print(text_content, end='')
                    contents.append(text_content)
```

**Gotcha:** unlike the Interactions / Anthropic / OpenAI-Responses streams, every `data:` chunk
here is a full `generateContent`-shaped object (candidates → content → parts); just keep
concatenating the parts' text. The same `candidates[0].content.parts` extraction works for both the
sync and streaming responses.

**Docs:** https://ai.google.dev/api/generate-content
</details>
