import datetime
import time
import threading
from typing import Any, Dict, List, Callable
from openai import OpenAI
import os
import json
import logging
from dotenv import load_dotenv
from .core.config import settings
from .repositories.twilio_repository import TwilioRepository
from .db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from .schemas.thread import ThreadCreate

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# # Global state - moved outside the class
# user_threads: Dict[str, str] = {}  # Store thread IDs for each user
# active_runs: Dict[str, str] = {}  # Track active runs for each thread

# Add global locks for thread-safe operations
threads_lock = threading.RLock()  # For user_threads dict
runs_lock = threading.RLock()  # For active_runs dict


class AssistantManager:
    def __init__(self, api_key: str, assistant_id: str, db: Session = Depends(get_db)):
        """Initialize the AssistantManager with API key and assistant ID."""
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.twilio_repo = TwilioRepository(db)
        # Cache function mappings to avoid recreating on each tool call
        self._function_mapping = None
        # Cache for thread IDs to reduce database calls
        self._thread_cache = {}
        # Cache for active runs to reduce database calls
        self._active_runs_cache = {}
        # Cache for assistant responses
        self._response_cache = {}
        # Cache TTL in seconds (5 minutes)
        self._cache_ttl = 300

    def get_or_create_thread(self, user_id: str) -> str:
        """Get existing thread for user or create new one."""
        with threads_lock:
            # Check cache first
            if user_id in self._thread_cache:
                thread_id, timestamp = self._thread_cache[user_id]
                if time.time() - timestamp < self._cache_ttl:
                    return thread_id

            logger.info(f"Checking existing thread for user: {user_id}")
            existing_thread = self.twilio_repo.get_thread_by_number(user_id)
            if existing_thread:
                logger.info(f"Found existing thread: {existing_thread.thread_id}")
                # Update cache
                self._thread_cache[user_id] = (existing_thread.thread_id, time.time())
                return existing_thread.thread_id

            logger.info(f"Creating new thread for user: {user_id}")
            thread = self.client.beta.threads.create()
            self.twilio_repo.create_thread(
                ThreadCreate(mobile_number=user_id, thread_id=thread.id)
            )
            # Update cache
            self._thread_cache[user_id] = (thread.id, time.time())
            return thread.id

    def get_active_run(self, thread_id: str) -> str:
        """Retrieve active run ID for a thread."""
        with runs_lock:
            # Check cache first
            if thread_id in self._active_runs_cache:
                run_id, timestamp = self._active_runs_cache[thread_id]
                if time.time() - timestamp < self._cache_ttl:
                    return run_id

            run_id = self.twilio_repo.get_active_run(thread_id)
            if run_id:
                # Update cache
                self._active_runs_cache[thread_id] = (run_id, time.time())
            return run_id

    def store_active_run(self, thread_id: str, run_id: str) -> None:
        """Store the active run for a thread."""
        with runs_lock:
            logger.info(f"Storing active run {run_id} for thread {thread_id}")
            self.twilio_repo.store_active_run(thread_id, run_id)
            # Update cache
            self._active_runs_cache[thread_id] = (run_id, time.time())

    def delete_active_run(self, thread_id: str) -> None:
        """Delete active run when completed or failed."""
        with runs_lock:
            logger.info(f"Deleting active run for thread {thread_id}")
            self.twilio_repo.delete_active_run(thread_id)
            # Clear cache
            self._active_runs_cache.pop(thread_id, None)

    def cleanup_active_run(self, thread_id: str) -> None:
        """Clean up any existing active run for a thread."""
        with runs_lock:
            run_id = self.get_active_run(thread_id)
            if run_id:
                try:
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
                    self.delete_active_run(thread_id)

    def add_message_to_thread(self, user_id: str, question: str) -> None:
        """Add a message to the user's thread with active run check."""
        thread_id = self.get_or_create_thread(user_id)
        logger.debug(f"thread {thread_id} for user {user_id} and question: {question} ")

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question = f"{question}\n\n(Current Date and Time: {current_datetime})"

        # Optimized retry logic with exponential backoff
        max_retries = 3
        base_delay = 0.5
        max_delay = 2.0

        for attempt in range(max_retries):
            try:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id, role="user", content=question
                )
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)  # Exponential backoff with cap
                    logger.warning(f"Retry {attempt + 1}/{max_retries} adding message: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to add message after {max_retries} attempts: {e}")
                    raise

    def run_conversation(self, user_id: str, question: str) -> str:
        """Run a conversation turn with thread safety and optimized error handling."""
        thread_id = self.get_or_create_thread(user_id)
        max_retries = 3
        base_delay = 0.5
        max_delay = 2.0

        # Use a thread-specific lock to prevent simultaneous operations
        thread_lock = threading.Lock()

        with thread_lock:
            if not settings.OPENAI_API_KEY or not self.assistant_id:
                logger.error("Missing OpenAI credentials")
                return "Configuration error: API credentials missing. Please contact support."

            for attempt in range(max_retries):
                try:
                    self.cleanup_active_run(thread_id)
                    self.add_message_to_thread(user_id, question)

                    # Start a new run with optimized polling
                    run = self.client.beta.threads.runs.create(
                        thread_id=thread_id, assistant_id=self.assistant_id
                    )
                    self.store_active_run(thread_id, run.id)

                    # Optimized polling with adaptive intervals
                    timeout = 180
                    start_time = time.time()
                    base_interval = 0.5
                    max_interval = 5.0
                    current_interval = base_interval

                    while time.time() - start_time < timeout:
                        run = self.client.beta.threads.runs.retrieve(
                            thread_id=thread_id, run_id=run.id
                        )

                        if run.status == "completed":
                            self.delete_active_run(thread_id)
                            return self.get_latest_assistant_response(user_id)
                        elif run.status == "requires_action":
                            self.handle_tool_calls(
                                thread_id,
                                run.id,
                                run.required_action.submit_tool_outputs.tool_calls,
                                user_id,
                            )
                            current_interval = base_interval  # Reset interval after action
                        elif run.status in ["failed", "expired", "cancelled"]:
                            self.cleanup_active_run(thread_id)
                            return f"Error: {run.status}"

                        time.sleep(current_interval)
                        current_interval = min(current_interval * 1.2, max_interval)  # Gradual increase

                    self.cleanup_active_run(thread_id)
                    return "I'm sorry, but your request is taking longer than expected. Please try again with a simpler question."

                except Exception as e:
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
                        self.cleanup_active_run(thread_id)
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
                AppointmentSuggestion,
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
                    get_products(**args)
                    if args
                    else get_products(args.get("siteCd"))
                ),
                "getOrders": lambda args: get_orders(f"+{user_id}"),
                "get_old_orders": lambda args: (
                    get_old_orders(**args) if args else get_old_orders()
                ),
                # Functions with specific required parameters
                "getEmployees": lambda args: get_employee(
                    args.get("items"), args.get("siteCd"),args.get("week")
                ),
                "AppointmentSuggestion": lambda args: AppointmentSuggestion(
                    week=args.get("week"),
                    employeeid=args.get("employeeId"),
                    itemno=args.get("itemNo"),
                    siteCd=args.get("siteCd"),
                ),
                "bookAppointment": lambda args: book_appointment(
                    beginTs=args.get("beginTs"),
                    durationMillis=args.get("durationMillis"),
                    mobileNumber=f"+{user_id}",
                    employeeId=args.get("employeeId"),
                    itemNo=args.get("itemNo"),
                    siteCd=args.get("siteCd"),
                ),
                "cancelAppointment": lambda args: cancel_appointment(
                    orderId=args.get("orderId"),
                    mobileNumber=f"+{user_id}",
                    siteCd=args.get("siteCd"),
                ),
                # "getProfile": lambda args: get_profile(
                #     args.get(
                #         "mobile_number",
                #         f"+{user_id}",
                #     )
                # ),
                "getProfile": lambda args: get_profile(f"+{user_id}"),
                # Support both function names for store_profile
                "updateProfile": lambda args: store_profile(
                    f"+{user_id}",
                    args.get("email", ""),
                    args.get("gender", ""),
                    args.get("fullNm", ""),
                    args.get("first_name", ""),
                    args.get("last_name", ""),
                ),
                # Add direct mapping for store_profile (same function, different name)
                "store_profile": lambda args: store_profile(
                    f"+{user_id}",
                    args.get("email", ""),
                    args.get("gender", ""),
                    args.get("fullNm", ""),
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
        """Handle tool calls with thread safety, improved error handling and performance."""
        tool_outputs = []
        function_mapping = self._get_function_mapping(user_id)

        start_time = time.time()
        total_tool_calls = len(tool_calls)
        logger.info(f"Processing {total_tool_calls} tool calls for thread {thread_id}")

        # Check if run is still active before processing tools

        # Process all tool calls
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
            self.client.beta.threads.runs.submit_tool_outputs_and_poll(
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
        """Get the latest assistant response with caching."""
        thread_id = self.get_or_create_thread(user_id)
        
        # Check cache first
        cache_key = f"{thread_id}_{user_id}"
        if cache_key in self._response_cache:
            response, timestamp = self._response_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return response

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages.data:
            if message.role == "assistant":
                response = message.content[0].text.value
                # Update cache
                self._response_cache[cache_key] = (response, time.time())
                return response

        return "No response found."


# Test function for basic chatbot interaction
def test_chatbot():
    """Function to test chatbot without any tool integration."""
    global user_threads
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
                with threads_lock:
                    user_threads.clear()
                print("Started new conversation")
                continue
            elif not question:
                continue

            print("Processing your request...")
            response = assistant_manager.run_conversation("923188335998", question)
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
