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

import datetime
import time
import threading
import functools
import json
import logging
from typing import Any, Dict, List, Callable
from openai import OpenAI
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repositories.twilio_repository import TwilioRepository
from app.schemas.thread import ThreadCreate
import backoff

logger = logging.getLogger(__name__)

# Shared locks for threads and runs
threads_lock = threading.RLock()
runs_lock = threading.RLock()
thread_locks: Dict[str, threading.Lock] = {}  # Real thread-safe per-user lock

def get_thread_lock(thread_id: str) -> threading.Lock:
    """Get or create a lock for a specific thread."""
    if thread_id not in thread_locks:
        thread_locks[thread_id] = threading.Lock()
    return thread_locks[thread_id]


class AssistantManager:
    def __init__(self, api_key: str, assistant_id: str):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self._function_mapping = None

    def set_db(self, db: Session):
        """Set DB session per-request."""
        self.twilio_repo = TwilioRepository(db)

    def get_or_create_thread(self, user_id: str) -> str:
        with threads_lock:
            logger.debug(f"Checking thread for user {user_id}")
            thread = self.twilio_repo.get_thread_by_number(user_id)
            if thread:
                return thread.thread_id

            logger.info(f"Creating new thread for user: {user_id}")
            thread = self.client.beta.threads.create()
            self.twilio_repo.create_thread(
                ThreadCreate(mobile_number=user_id, thread_id=thread.id)
            )
            return thread.id

    def get_active_run(self, thread_id: str) -> str:
        with runs_lock:
            return self.twilio_repo.get_active_run(thread_id)

    def store_active_run(self, thread_id: str, run_id: str) -> None:
        with runs_lock:
            self.twilio_repo.store_active_run(thread_id, run_id)

    def delete_active_run(self, thread_id: str) -> None:
        with runs_lock:
            self.twilio_repo.delete_active_run(thread_id)

    def cleanup_active_run(self, thread_id: str) -> None:
        with runs_lock:
            run_id = self.get_active_run(thread_id)
        if not run_id:
            return

        try:
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.status in ["queued", "in_progress", "requires_action"]:
                self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
        except Exception as e:
            logger.error(f"Error cleaning up run: {e}")
        finally:
            self.delete_active_run(thread_id)

    @backoff.on_exception(backoff.expo, Exception, max_tries=3, max_time=10)
    def add_message_to_thread(self, user_id: str, question: str) -> None:
        thread_id = self.get_or_create_thread(user_id)
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question = f"{question}\n\n(Current Date and Time: {current_datetime})"
        self.client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=question
        )

    def run_conversation(self, user_id: str, question: str, receiver_number: str) -> str:
        thread_id = self.get_or_create_thread(user_id)
        lock = get_thread_lock(thread_id)

        with lock:
            if not settings.OPENAI_API_KEY or not self.assistant_id:
                return "Assistant is not configured properly. Please contact support."

            self.cleanup_active_run(thread_id)
            self.add_message_to_thread(user_id, question)

            try:
                run = self.client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant_id
                )
                self.store_active_run(thread_id, run.id)
            except Exception as e:
                logger.error(f"Error creating run: {e}")
                return f"Error starting assistant: {str(e)}"

            timeout = 180
            start = time.time()
            backoff_interval = 0.5

            while time.time() - start < timeout:
                run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

                if run.status == "completed":
                    self.delete_active_run(thread_id)
                    return self.get_latest_assistant_response(user_id)

                elif run.status == "requires_action":
                    self.handle_tool_calls(
                        thread_id,
                        run.id,
                        run.required_action.submit_tool_outputs.tool_calls,
                        user_id,
                        receiver_number
                    )
                    backoff_interval = 0.5

                elif run.status in ["failed", "expired", "cancelled"]:
                    self.cleanup_active_run(thread_id)
                    return f"Run ended with status: {run.status}"

                time.sleep(backoff_interval)
                backoff_interval = min(5, backoff_interval * 1.5)

            self.cleanup_active_run(thread_id)
            return "Sorry, this is taking too long. Try again later."

    def get_latest_assistant_response(self, user_id: str) -> str:
        thread_id = self.get_or_create_thread(user_id)
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id, order="desc", limit=1
            )
            if messages and messages.data:
                for content in messages.data[0].content:
                    if content.type == "text":
                        return content.text.value
            return "No assistant response found."
        except Exception as e:
            logger.error(f"Error fetching assistant response: {e}")
            return "Unable to fetch assistant response."

    def _load_function_mapping(self, user_id: str, receiver_number: str) -> Dict[str, Callable]:
        from app.utils.tools_wrapper_util import (
            get_sites, get_products, get_employee,
            AppointmentSuggestion, book_appointment,
            cancel_appointment, get_profile, store_profile,
            get_orders, get_old_orders,
        )
        return {
            "getSites": lambda args: get_sites(),
            "getProducts": lambda args: (
                get_products(**args) if args else get_products(args.get("siteCd"))
            ),
            "getOrders": lambda args: get_orders(f"+{user_id}"),
            "get_old_orders": lambda args: (
                get_old_orders(**args) if args else get_old_orders()
            ),
            "getEmployees": lambda args: get_employee(
                args.get("items"), args.get("siteCd"), args.get("week")
            ),
            "AppointmentSuggestion": lambda args: AppointmentSuggestion(
                customerCd=args.get("customerCd"),
                siteCd=args.get("siteCd"),
                week=args.get("week"),
                positions=args.get("positions")
            ),
            "bookAppointment": lambda args: book_appointment(
                receiver_nunmber=receiver_number,
                mobileNumber=f"+{user_id}",
                siteCd=args.get("siteCd"),
                customerId=args.get("customerId"),
                reminderSms=args.get("reminderSms", True),
                reminderEmail=args.get("reminderEmail", False),
                positions=[
                    {
                        "ordinalPosition": i + 1,
                        "beginTs": pos.get("beginTs"),
                        "durationMillis": pos.get("durationMillis"),
                        "employeeId": pos.get("employeeId"),
                        "itemNo": pos.get("itemNo"),
                        "itemNm": pos.get("itemNm")
                    }
                    for i, pos in enumerate(args.get("positions", []))
                ]
            ),
            "cancelAppointment": lambda args: cancel_appointment(
                orderId=args.get("orderId"),
                mobileNumber=f"+{user_id}",
                siteCd=args.get("siteCd")
            ),
            "getProfile": lambda args: get_profile(f"+{user_id}"),
            "updateProfile": lambda args: store_profile(
                f"+{user_id}",
                args.get("email", ""),
                args.get("gender", ""),
                args.get("fullNm", ""),
                args.get("fullNm", ""),
                args.get("first_name", ""),
                args.get("last_name", ""),
                args.get("dplAccepted", 0)
            ),
            "store_profile": lambda args: store_profile(
                f"+{user_id}",
                args.get("email", ""),
                args.get("gender", ""),
                args.get("fullNm", ""),
                args.get("fullNm", ""),
                args.get("first_name", ""),
                args.get("last_name", ""),
                args.get("dplAccepted", 0)
            )
        }

    def handle_tool_calls(
        self,
        thread_id: str,
        run_id: str,
        tool_calls: List[Dict[str, Any]],
        user_id: str,
        receiver_number: str
    ) -> None:
        outputs = []
        if not self._function_mapping:
            self._function_mapping = self._load_function_mapping(user_id, receiver_number)

        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments or "{}")
                handler = self._function_mapping.get(function_name)

                if not handler:
                    logger.warning(f"No handler for function: {function_name}")
                    outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": f"No function found for {function_name}"})
                    })
                    continue

                result = handler(arguments)
                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result)
                })

            except Exception as e:
                logger.error(f"Error processing tool call {tool_call.id}: {e}")
                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({"error": str(e)})
                })

        try:
            self.client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=outputs
            )
        except Exception as e:
            logger.error(f"Failed to submit tool outputs: {e}")
            try:
                self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
            except Exception as cancel_err:
                logger.error(f"Error cancelling run after failed tool submit: {cancel_err}")
