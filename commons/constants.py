"""
Configuration constants for AI service integrations.

This module centralizes all API endpoints, API keys, and default configuration
values used across different AI service providers (OpenAI, Anthropic, Gemini).

All API keys are loaded from environment variables for security.
"""

import os

# Default system prompt used across all AI services
DEFAULT_SYSTEM_PROMPT = "You are an assistant who answers concisely and informatively."

# OpenAI API configuration
# Base URL the OpenAI SDK uses as its `base_url`; custom clients append the path
# (e.g. "/chat/completions", "/responses", "/embeddings").
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_CHAT_COMPLETIONS_ENDPOINT = f"{OPENAI_BASE_URL}/v1/chat/completions"
OPENAI_RESPONSES_ENDPOINT = f"{OPENAI_BASE_URL}/v1/responses"
OPENAI_EMBEDDINGS_ENDPOINT = f"{OPENAI_BASE_URL}/v1/embeddings"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GPT_5_4_MINI="gpt-5.4-mini"
GPT_5_5="gpt-5.5"

# Anthropic API configuration
# Base URL the Anthropic SDK uses as its `base_url`; the custom client appends
# "/v1/messages".
ANTHROPIC_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_ENDPOINT = f"{ANTHROPIC_BASE_URL}/v1/messages"
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ANTHROPIC_HAIKU_4_5 = "claude-haiku-4-5"

# Google Gemini API configuration
# Base URL the google-genai SDK uses as its `base_url` (with api_version "v1beta");
# custom clients append "/v1beta/models/{model}:generateContent",
# "/v1beta/models/{model}:streamGenerateContent" or "/v1beta/interactions".
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com"
GEMINI_ENDPOINT = f"{GEMINI_BASE_URL}/v1beta/models"
GEMINI_API_REVISION = "2026-05-20"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_3_FLASH='gemini-3-flash-preview'

# User Service API configuration
USER_SERVICE_ENDPOINT = "http://localhost:8041"