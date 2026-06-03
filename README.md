## About the Course

This is a **Python course** focused on building AI-powered applications by working directly with APIs. 
Instead of relying on tools like LangChain that abstract away the internals, we go straight to the API level. By the
end, when you do use frameworks, you'll understand exactly what's happening under the hood.

**What this course IS:**

- API-first approach to building AI applications
- 80% hands-on practice with real-world tasks, no "Hello World" exercises
- A challenging journey that mirrors actual AI application development work

**What this course is NOT:**

- Not an ML course: we won't dive into transformers, training, or how LLMs work internally
- Not a prompt engineering course: we expect you to already know how to write prompts and understand that different
  models behave differently with the same input


> ⚠️ This is not an easy course. You will be building the same things professional AI developers build daily.

> 💡 What you get from this course depends on you. We designed it as a practical reference you can return to and reuse in your daily work.

> 🤝 Need help along the way? Join the [Community on Discord]() — we have dedicated course support channels. After joining, add the role shown below to unlock them.

> 🚨 Pay attention that in the course we have repetitive tasks (to create agent, clients, etc.) — it's done intentionally!

## Branches Structure

- `main` - tasks with descriptions
- `main-detailed` - tasks with super detailed descriptions
- `completed` - completed tasks, useful when stuck

---

## Prerequisites

- **Python 3.11+**
- **IDE** (PyCharm, VS Code, or any preferred editor)
- **Postman** (for testing API calls)
- **Docker** with Docker Compose
- **API Keys** to work with different models (you will need to pay ~5-10$ credits):
  - **OpenAI API Key** (we will be primarily working with OpenAI models). [Generate it here](https://platform.openai.com/settings/organization/api-keys) and set up as environment variable with name `OPENAI_API_KEY`
  - **Anthropic API Key** [Generate it here](https://platform.claude.com/settings/keys) and set up as environment variable with name `ANTHROPIC_API_KEY`
  - **Gemini API Key** [Generate it here](https://aistudio.google.com/app/api-keys) and set up as environment variable with name `GEMINI_API_KEY`

---

## Getting Started

### 0. ⭐️ **Star the repository** - it will help us grow ⭐️

### 1. ⑃ Fork and clone the repository

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

