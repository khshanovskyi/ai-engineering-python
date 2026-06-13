from t1_llm_api._models.conversation import Conversation
from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.base_client import AIClient


async def start(stream: bool, client: AIClient) -> None:
    """
    Start an interactive chat session with an AI client.

    This function runs a continuous loop that:
    1. Prompts the user for input
    2. Sends the conversation history to the AI
    3. Displays the AI's response
    4. Maintains conversation context

    The loop continues until the user types 'exit'.

    Args:
        stream (bool): If True, use streaming responses (real-time token display).
                      If False, use synchronous responses (complete response at once).
        client (AIClient): The AI client instance to use for generating responses.
    """
    #TODO:
    # - create a Conversation() to hold the running message history
    # - print a hint telling the user to type 'exit' to quit
    # - loop:
    #   - read user input (input(...)) and strip it
    #   - if it equals 'exit' (case-insensitive), print a goodbye and break
    #   - wrap it in Message(Role.USER, ...) and add it to the conversation
    #   - print the "🤖: " prefix without a trailing newline (end="")
    #   - if `stream`: await client.stream_response(conversation.get_messages())
    #     else: client.response(conversation.get_messages())
    #   - add the returned ai_message back to the conversation
    raise NotImplementedError()
