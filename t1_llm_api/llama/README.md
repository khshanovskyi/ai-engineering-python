# Bonus: Run a local Llama in Docker — reuse the clients you already built

So far every client has talked to a paid cloud API. Here you run a **small Llama model locally** (no API key, no cost)
in Docker and drive it with the **same clients you already implemented**.

The trick: [Ollama](https://ollama.com) serves one local model behind **three compatible API surfaces at once**, so our
existing clients fit with no change:

| Surface                 | Endpoint (port 11434)                 | Client                        |
|-------------------------|---------------------------------------|-------------------------------|
| OpenAI Chat Completions | `POST /v1/chat/completions`           | `OpenAIChatCompletionsClient` |
| OpenAI Responses        | `POST /v1/responses`                  | `OpenAIResponsesClient`       |
| Anthropic Messages      | `POST /v1/messages` (Ollama ≥ 0.14.0) | `AnthropicAIClient`           |

---

## 1. Start Llama with Docker Compose

> ⚠️ **This is heavy.** The image + model download is a ~5GB, and the model runs on your machine. Give it time on the first start.

From this directory (`t1_llm_api/llama/`):

```bash
docker compose up -d
```

This starts Ollama on port **11434** and pulls **`llama3.2:1b`** (the smallest, fastest model). Watch the download
finish:

```bash
docker compose logs -f puller
```

---

## 2. Play with the different clients

Open [`llama_app.py`](llama_app.py). It already builds all three clients pointed at
`localhost:11434`:

- `chat_completions_client` — OpenAI Chat Completions surface
- `responses_client` — OpenAI Responses surface
- `anthropic_client` — Anthropic Messages surface

The last line picks which one to chat with:

```python
asyncio.run(
    start(True, anthropic_client)  # swap in chat_completions_client / responses_client
)
```

Run it from the **repo root**:

```bash
python -m t1_llm_api.llama.llama_app
```

> ⏳ The **first** request loads the model into memory, so it takes a while. From the
> **second** request on it's much faster.

---

## 3. Confirm which endpoint was hit — read the container logs

While you chat, tail the Ollama container's logs in another terminal:

```bash
docker compose logs -f ollama
```

Each request prints the path Ollama served, so you can verify the client really reached the surface you expected:

```
[GIN] ... | POST "/v1/chat/completions"
[GIN] ... | POST "/v1/responses"
[GIN] ... | POST "/v1/messages"
```

---

## Cleanup

```bash
docker compose down      # stop & remove containers (keeps the downloaded model)
docker compose down -v   # also delete the downloaded model volume
```