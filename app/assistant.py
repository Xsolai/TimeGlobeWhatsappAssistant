from .agent import AssistantManager
from .core.config import settings

assistant_manager = AssistantManager(
    settings.OPENAI_API_KEY, settings.OPENAI_ASSISTANT_ID
)


def get_response_from_gpt(msg, user_id):
    response = assistant_manager.run_conversation(user_id, msg)
    print(f"Response for user {user_id}: {response}")
    return response
