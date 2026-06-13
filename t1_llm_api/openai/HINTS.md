# HINTS — openai/base (Bearer-token base client)

Detailed guidance for the TODOs in `base.py`. Try the stub first; expand a section when stuck.

<details>
<summary><code>base.py</code> — <code>BaseOpenAIClient.__init__()</code> · validate the key + Bearer-format it</summary>

**What you're building:** the OpenAI-specific base class that all OpenAI clients
(Chat Completions + Responses, SDK + custom) extend. Its one job is to **validate the key and
format it as an `Authorization` header value** before handing it to `AIClient.__init__`.

**Steps:**
1. Validate `api_key`: if it's `None`, empty, or only whitespace, `raise ValueError(...)`.
   (The parent `AIClient` validates too, but it would store the *Bearer-prefixed* string, so do
   it here against the raw key for a clear message.)
2. Call `super().__init__(...)` forwarding `base_url`, `model_name`, `system_prompt`, **and the
   key formatted as** `f"Bearer {api_key}"`.

**Key snippet:**
```python
if not api_key or api_key.strip() == "":
    raise ValueError("API key cannot be null or empty")
super().__init__(
    base_url=base_url,
    model_name=model_name,
    system_prompt=system_prompt,
    api_key=f"Bearer {api_key}",   # <-- the lesson: store the full header value
)
```

**Why the `Bearer ` prefix here?**
- The **custom (raw-HTTP) clients** send `headers={"Authorization": self._api_key, ...}`. Because
  `self._api_key` already equals `"Bearer sk-..."`, they can drop it straight into the header with
  no extra string-building. That's the whole point of formatting it once, centrally.
- The **SDK clients** (`OpenAIChatCompletionsClient`, `OpenAIResponsesClient`) do *not* use
  `self._api_key` — they pass the **raw** `api_key` argument to `OpenAI(api_key=...)`, and the SDK
  adds `Bearer ` for you. So `__init__` keeps the raw `api_key` parameter around for the SDK and
  stores the Bearer-formatted version on `self._api_key` for the custom path. (See
  `chat/completions/HINTS.md` and `responses/HINTS.md`.)

**Gotchas:**
- Note the argument order: `AIClient.__init__(self, base_url, model_name, api_key, system_prompt)`
  but `BaseOpenAIClient.__init__(self, base_url, model_name, system_prompt, api_key)`. Forward by
  **keyword** (as above) so you don't transpose `api_key` and `system_prompt`.
- `OPENAI_BASE_URL` already includes `/v1`; the SDK accepts it as `base_url`, and custom clients
  append the path (`/chat/completions`, `/responses`). Don't add a second `/v1`.
- This is an `ABC` with no abstract methods of its own — it only exists to share the key handling.
</details>
