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
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
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
        logger.info(f"All User threads: {self.user_threads}")
        if user_id not in self.user_threads:
            thread = self.client.beta.threads.create()
            self.user_threads[user_id] = thread.id
        return self.user_threads[user_id]

    def cleanup_active_run(self, thread_id: str) -> None:
        """Clean up any existing active run for a thread."""
        logger.debug(f"Active Runs Before Cleanup : {self.active_runs}")
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
                logger.debug(f"All Active Runs After Cleanup: {self.active_runs}")

    def add_message_to_thread(self, user_id: str, question: str) -> None:
        """Add a message to the user's thread with active run check."""
        thread_id = self.get_or_create_thread(user_id)
        logger.debug(
            f"thread {thread_id} for user {user_id}  and question: {question} "
        )
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
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} adding message: {e}"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to add message after {max_retries} attempts: {e}"
                    )
                    raise

    def run_conversation(self, user_id: str, question: str) -> str:
        """Run a conversation turn with optimized error handling and run status management."""
        thread_id = self.get_or_create_thread(user_id)
        max_retries = 3
        retry_delay = 0.5
        logger.debug(f"All Threads {self.active_runs}")
        # Debug log OpenAI config
        logger.info(
            f"OpenAI API key length: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}"
        )
        logger.info(f"Assistant ID: {self.assistant_id}")

        if not settings.OPENAI_API_KEY or not self.assistant_id:
            logger.error(
                "Missing OpenAI credentials: API key or Assistant ID not configured"
            )
            return (
                "Configuration error: API credentials missing. Please contact support."
            )

        for attempt in range(max_retries):
            try:
                self.cleanup_active_run(thread_id)
                # Reduced unnecessary delay
                self.add_message_to_thread(user_id, question)

                # Start a new run with detailed logging
                logger.info(
                    f"Creating new run for thread {thread_id} with assistant {self.assistant_id}"
                )
                try:
                    run = self.client.beta.threads.runs.create(
                        thread_id=thread_id, assistant_id=self.assistant_id
                    )
                    logger.info(f"Run created successfully: {run.id}")
                    self.active_runs[thread_id] = run.id
                except Exception as run_error:
                    logger.error(f"Error creating run: {run_error}")
                    return f"Unable to process your request: {str(run_error)}"

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
                        error_msg = getattr(
                            run, "last_error", {"message": f"Run {run.status}"}
                        )
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

            # Define properly typed function handlers with correct parameter unpacking
            self._function_mapping = {
                # Simple functions with one or no parameters
                "getSites": lambda args: get_sites(),
                "getProducts": lambda args: (
                    get_products(**args) if args else get_products()
                ),
                "getOrders": lambda args: get_orders(),
                "get_old_orders": lambda args: (
                    get_old_orders(**args) if args else get_old_orders()
                ),
                # Functions with specific required parameters
                "getEmployees": lambda args: get_employee(
                    args.get("item_no"), args.get("item_name")
                ),
                "AppointmentSuggestion": lambda args: get_suggestions(
                    args.get("employee_id"), args.get("item_no")
                ),
                "bookAppointment": lambda args: book_appointment(
                    args.get("duration"), args.get("user_date_time")
                ),
                "cancelAppointment": lambda args: cancel_appointment(
                    args.get("order_id")
                ),
                "getProfile": lambda args: get_profile(
                    args.get(
                        "mobile_number",
                        user_id[9:] if user_id.startswith("whatsapp:") else "",
                    )
                ),
                # Support both function names for store_profile
                "updateProfile": lambda args: store_profile(
                    args.get("mobile_number", ""),
                    args.get("email", ""),
                    args.get("gender", ""),
                    args.get("first_name", ""),
                    args.get("last_name", ""),
                ),
                # Add direct mapping for store_profile (same function, different name)
                "store_profile": lambda args: store_profile(
                    args.get("mobile_number", ""),
                    args.get("email", ""),
                    args.get("gender", ""),
                    args.get("first_name", ""),
                    args.get("last_name", ""),
                ),
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

        start_time = time.time()
        total_tool_calls = len(tool_calls)
        logger.info(f"Processing {total_tool_calls} tool calls for thread {thread_id}")

        # Process all tool calls in parallel (if supported)
        for idx, tool_call in enumerate(tool_calls):
            tool_start_time = time.time()
            try:
                function_name = tool_call.function.name
                raw_args = tool_call.function.arguments

                # Debug log for function name
                logger.info(f"Function name requested: '{function_name}'")
                logger.info(f"Available functions: {list(function_mapping.keys())}")

                # Safely parse arguments
                try:
                    arguments = json.loads(raw_args) if raw_args else {}
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse arguments: {raw_args}")
                    arguments = {}

                # Log tool call details
                arg_string = ", ".join([f"{k}={v}" for k, v in arguments.items()])
                logger.info(
                    f"Tool {idx+1}/{total_tool_calls}: Executing {function_name}({arg_string})"
                )

                handler = function_mapping.get(function_name)
                if handler:
                    try:
                        result = handler(arguments)
                        tool_execution_time = time.time() - tool_start_time
                        result_status = result.get("status", "unknown")
                        logger.info(
                            f"Tool {idx+1}/{total_tool_calls}: {function_name} completed with status '{result_status}' in {tool_execution_time:.2f}s"
                        )
                    except TypeError as e:
                        # Handle parameter mismatches more gracefully
                        logger.error(f"Parameter mismatch in {function_name}: {e}")
                        result = {
                            "status": "error",
                            "message": f"Parameter error: {str(e)}",
                        }
                else:
                    # Check for case-insensitive matches
                    case_insensitive_match = next(
                        (
                            k
                            for k in function_mapping.keys()
                            if k.lower() == function_name.lower()
                        ),
                        None,
                    )

                    if case_insensitive_match:
                        logger.warning(
                            f"Case mismatch in function name. Using '{case_insensitive_match}' instead of '{function_name}'"
                        )
                        try:
                            result = function_mapping[case_insensitive_match](arguments)
                            tool_execution_time = time.time() - tool_start_time
                            logger.info(
                                f"Tool {idx+1}/{total_tool_calls}: {case_insensitive_match} completed in {tool_execution_time:.2f}s"
                            )
                        except Exception as e:
                            logger.error(
                                f"Error executing case-insensitive match {case_insensitive_match}: {e}"
                            )
                            result = {"status": "error", "message": f"Error: {str(e)}"}
                    else:
                        result = {"error": f"Function {function_name} not implemented"}
                        logger.warning(
                            f"Tool {idx+1}/{total_tool_calls}: Unimplemented function called: {function_name}"
                        )

                        # Suggest alternatives for typos
                        similar_functions = [
                            k
                            for k in function_mapping.keys()
                            if any(c in k.lower() for c in function_name.lower())
                        ]
                        if similar_functions:
                            logger.info(
                                f"Similar functions that might match: {similar_functions}"
                            )

                # Log result summary if not too large
                if isinstance(result, dict):
                    result_keys = list(result.keys())
                    logger.debug(f"Tool {idx+1} result keys: {result_keys}")

                tool_outputs.append(
                    {"tool_call_id": tool_call.id, "output": json.dumps(result)}
                )

            except Exception as e:
                tool_execution_time = time.time() - tool_start_time
                logger.error(
                    f"Tool {idx+1}/{total_tool_calls}: Error in {tool_call.function.name}: {str(e)} after {tool_execution_time:.2f}s"
                )
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)}),
                    }
                )

        try:
            submission_start = time.time()
            self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs
            )
            submission_time = time.time() - submission_start
            total_time = time.time() - start_time
            logger.info(
                f"Tool outputs submitted successfully in {submission_time:.2f}s (total tool handling: {total_time:.2f}s)"
            )
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Error submitting tool outputs after {total_time:.2f}s: {e}")
            # Attempt to cancel the run if submitting tool outputs fails
            try:
                self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
                logger.info(
                    f"Run {run_id} cancelled after tool output submission failure"
                )
            except Exception as cancel_error:
                logger.error(
                    f"Failed to cancel run after submission error: {cancel_error}"
                )

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
