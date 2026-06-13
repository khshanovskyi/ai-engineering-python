# HINTS — base_app (interactive REPL)

Detailed guidance for the TODOs in `base_app.py`. Try the stub first; expand a section when stuck.

This is the shared chat loop used by **every** provider app. Each `*_app.py` builds a
client and calls `asyncio.run(start(<stream_bool>, <client>))`, so this one function drives
OpenAI, Anthropic and Gemini alike. It never knows which provider it's talking to — it only
depends on the `AIClient` contract (`response` / `stream_response`) from `base_client.py`.

<details>
<summary><code>base_app.py</code> — <code>start(stream, client)</code> · the shared interactive chat loop</summary>

**What you're building:** a console loop that keeps a running `Conversation`, sends the full
history to the client each turn, prints the reply, and stores it back so context accumulates.

**Steps:**
1. Create a `Conversation()` (from `t1_llm_api._models.conversation`). It owns the message
   list and hands you `add_message(...)` / `get_messages()`.
2. Print a one-line hint telling the user to type `exit` to quit.
3. Loop forever:
   1. Read a line with `input("➡️ ")` and `.strip()` it.
   2. If it equals `"exit"` (compare case-insensitively, e.g. `.lower()`), print a goodbye and `break`.
   3. Wrap the text in `Message(Role.USER, user_input)` and `conversation.add_message(...)` it.
   4. Print the assistant prefix **without a newline**: `print("🤖: ", end="")` so the reply
      streams on the same line.
   5. Branch on `stream`:
      - `True`  → `ai_message = await client.stream_response(conversation.get_messages())`
      - `False` → `ai_message = client.response(conversation.get_messages())`
   6. `conversation.add_message(ai_message)` so the assistant turn becomes part of history.

**Key snippet:**
```python
conversation = Conversation()
print("Type your question or 'exit' to quit.")
while True:
    user_input = input("➡️ ").strip()
    if user_input.lower() == "exit":
        print("Exiting the chat. Goodbye!")
        break

    conversation.add_message(Message(Role.USER, user_input))

    print("🤖: ", end="")
    if stream:
        ai_message = await client.stream_response(conversation.get_messages())
    else:
        ai_message = client.response(conversation.get_messages())

    conversation.add_message(ai_message)
```

**Gotchas:**
- `start` is `async` because `stream_response` is a coroutine you must `await`. The synchronous
  `response` path doesn't need `await`. Both must end up appending a `Message` to the conversation.
- You pass `conversation.get_messages()` (the **history list**) — not the raw string — so the
  model sees the whole dialogue every turn.
- The **system prompt is not added to the conversation here.** Each client injects
  `self._system_prompt` itself per request (OpenAI inlines a `system` message; Anthropic/Gemini
  use a dedicated field). Don't try to push it into `Conversation`.
- Printing tokens is the *client's* job (it does `print(..., end="")` as deltas arrive); `start`
  only prints the `🤖: ` prefix. Don't double-print the returned content.
</details>
