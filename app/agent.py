import datetime
import time
from typing import Any, Dict, List, Callable
from openai import OpenAI
import os
import json
import logging
from dotenv import load_dotenv
from .core.config import settings

# from tools.tools import check_profile, create_profile

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# print("Testing TimeGlobeService connection...")
# try:
#     sites = get_sites()
#     print(f"Successfully retrieved sites: {sites}")
# except Exception as e:
#     print(f"Error connecting to TimeGlobeService: {e}")


class AssistantManager:
    def __init__(self, api_key: str, assistant_id: str):
        """Initialize the AssistantManager with API key and assistant ID."""
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.user_threads: Dict[str, str] = {}  # Store thread IDs for each user
        self.active_runs: Dict[str, str] = {}  # Track active runs for each thread
        
        # Cache function mappings to avoid recreating on each tool call
        self._function_mapping = None

    def get_or_create_thread(self, user_id: str) -> str:
        """Get existing thread for user or create new one."""
        if user_id not in self.user_threads:
            thread = self.client.beta.threads.create()
            self.user_threads[user_id] = thread.id
        return self.user_threads[user_id]

    def cleanup_active_run(self, thread_id: str) -> None:
        """Clean up any existing active run for a thread."""
        if thread_id in self.active_runs:
            try:
                run_id = self.active_runs[thread_id]
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run_id
                )
                if run.status in ["queued", "in_progress", "requires_action"]:
                    self.client.beta.threads.runs.cancel(
                        thread_id=thread_id, run_id=run_id
                    )
            except Exception as e:
                logger.error(f"Error cleaning up run: {e}")
            finally:
                del self.active_runs[thread_id]

    def add_message_to_thread(self, user_id: str, question: str) -> None:
        """Add a message to the user's thread with active run check."""
        thread_id = self.get_or_create_thread(user_id)
        
        # No need to clean up run here as it's already done in run_conversation
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question = f"{question}\n\n(Current Date and Time: {current_datetime})"

        # Optimized retry logic with shorter initial delay
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id, role="user", content=question
                )
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} adding message: {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to add message after {max_retries} attempts: {e}")
                    raise

    def run_conversation(self, user_id: str, question: str) -> str:
        """Run a conversation turn with optimized error handling and run status management."""
        thread_id = self.get_or_create_thread(user_id)
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                self.cleanup_active_run(thread_id)
                # Reduced unnecessary delay
                self.add_message_to_thread(user_id, question)

                # Start a new run
                run = self.client.beta.threads.runs.create(
                    thread_id=thread_id, assistant_id=self.assistant_id
                )
                self.active_runs[thread_id] = run.id

                # More reasonable timeout - 60 seconds instead of 100
                timeout = 60
                start_time = time.time()
                # Optimized polling strategy
                backoff_interval = 0.5
                max_backoff = 5  # Cap max backoff at 5 seconds instead of 16

                while time.time() - start_time < timeout:
                    run = self.client.beta.threads.runs.retrieve(
                        thread_id=thread_id, run_id=run.id
                    )
                    logger.info(f"Run status: {run.status}")
                    
                    if run.status == "completed":
                        del self.active_runs[thread_id]
                        return self.get_latest_assistant_response(user_id)
                    elif run.status == "requires_action":
                        self.handle_tool_calls(
                            thread_id,
                            run.id,
                            run.required_action.submit_tool_outputs.tool_calls,
                            user_id,
                        )
                        # Reset backoff after handling tool calls since we expect a quick status change
                        backoff_interval = 0.5
                    elif run.status in ["failed", "expired", "cancelled"]:
                        logger.warning(f"Run ended with status: {run.status}")
                        self.cleanup_active_run(thread_id)
                        error_msg = getattr(run, 'last_error', {'message': f"Run {run.status}"})
                        return f"Sorry, I couldn't process your request: {error_msg.get('message', 'Unknown error')}"

                    time.sleep(backoff_interval)
                    backoff_interval = min(
                        max_backoff, backoff_interval * 1.5
                    )  # Gentler exponential backoff

                logger.error("Conversation run timed out")
                return "I'm sorry, but your request is taking longer than expected. Please try again with a simpler question."

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"All {max_retries} attempts failed: {e}")
                    return f"Sorry, I encountered an error: {str(e)}"

        return "Failed to complete the conversation after multiple attempts."

    def _get_function_mapping(self, user_id: str) -> Dict[str, Callable]:
        """Get cached function mapping or create a new one."""
        if self._function_mapping is None:
            # Import only once when needed rather than on every tool call
            from .utils.tools_wrapper_util import (
                get_sites,
                get_products,
                get_employee,
                get_suggestions,
                book_appointment,
                cancel_appointment,
                get_profile,
                store_profile,
                get_orders,
                get_old_orders,
            )
            
            self._function_mapping = {
                "getSites": lambda args=None: get_sites(),
                "getProducts": lambda args: get_products(**args) if args else get_products(),
                "getEmployees": lambda args: get_employee(**args) if args else get_employee(),
                "AppointmentSuggestion": lambda args: get_suggestions(**args) if args else get_suggestions(),
                "bookAppointment": lambda args: book_appointment(**args) if args else book_appointment(),
                "cancelAppointment": lambda args: cancel_appointment(**args) if args else cancel_appointment(),
                "updateProfile": lambda args: store_profile(**args) if args else store_profile(),
                "getProfile": lambda args: get_profile(**args) if args else get_profile(user_id[9:]),
                "getOrders": lambda args: get_orders(**args) if args else get_orders(),
                "get_old_orders": lambda args: get_old_orders(**args) if args else get_old_orders(),
            }
        
        return self._function_mapping

    def handle_tool_calls(
        self,
        thread_id: str,
        run_id: str,
        tool_calls: List[Dict[Any, Any]],
        user_id: str,
    ) -> None:
        """Handle tool calls with improved error handling and performance."""
        tool_outputs = []
        function_mapping = self._get_function_mapping(user_id)
        
        # Process all tool calls in parallel (if supported)
        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                logger.info(f"Executing function: {function_name} with arguments: {arguments}")

                handler = function_mapping.get(function_name)
                if handler:
                    result = handler(arguments)
                else:
                    result = {"error": f"Function {function_name} not implemented"}
                    logger.warning(f"Unimplemented function called: {function_name}")
                
                tool_outputs.append(
                    {"tool_call_id": tool_call.id, "output": json.dumps(result)}
                )

            except Exception as e:
                logger.error(f"Error in tool call {tool_call.function.name}: {str(e)}")
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)}),
                    }
                )

        try:
            self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs
            )
        except Exception as e:
            logger.error(f"Error submitting tool outputs: {e}")
            # Attempt to cancel the run if submitting tool outputs fails
            try:
                self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
            except:
                pass  # Already logged the primary error

    def get_latest_assistant_response(self, user_id: str) -> str:
        """Get the latest assistant response with error handling."""
        thread_id = self.user_threads.get(user_id)
        if not thread_id:
            return "No conversation thread found."

        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id, order="desc", limit=1
            )
            
            for msg in messages:
                if msg.role == "assistant":
                    # Handle different content types properly
                    for content_item in msg.content:
                        if content_item.type == "text":
                            return content_item.text.value
                    
                    # If we get here, no text content was found
                    return "Assistant responded but no text content was found."
            
            return "No response from assistant."
            
        except Exception as e:
            logger.error(f"Error retrieving assistant response: {e}")
            return "Error retrieving response."


# Test function for basic chatbot interaction
def test_chatbot():
    """Function to test chatbot without any tool integration."""
    api_key = settings.OPENAI_API_KEY
    logger.info(f"API key available: {bool(api_key)}")
    
    if not api_key:
        logger.error("Error: OPENAI_API_KEY environment variable not set")
        return

    assistant_id = settings.OPENAI_ASSISTANT_ID
    if not assistant_id:
        logger.error("Error: OPENAI_ASSISTANT_ID not set")
        return
        
    assistant_manager = AssistantManager(api_key, assistant_id)
    while True:
        try:
            question = input("\nYou: ").strip()
            if question.lower() == "exit":
                print("Goodbye!")
                break
            elif question.lower() == "new":
                assistant_manager.user_threads.clear()
                print("Started new conversation")
                continue
            elif not question:
                continue

            print("Processing your request...")
            response = assistant_manager.run_conversation("123", question)
            print(f"\nAssistant: {response}")

        except KeyboardInterrupt:
            print(
                "\nConversation interrupted. Type 'exit' to quit or continue with your next question."
            )
        except Exception as e:
            logger.exception("Error in chat loop")
            print(f"\nError: {str(e)}")
            print("You can continue with your next question or type 'exit' to quit.")


if __name__ == "__main__":
    test_chatbot()
