import datetime
import time
import threading
import json
from typing import Any, Dict, List, Callable, Optional
from openai import OpenAI
import os
import logging
from sqlalchemy.orm import Session
from .schemas.thread import ThreadCreate
from .repositories.conversation_repository import ConversationRepository
from .system_prompt import System_prompt
from .tools_schema import Tools
from .core.config import settings
from app.utils.message_queue import clean_last_tool_messages

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Thread-safe locks
threads_lock = threading.RLock()


class ChatAgent:
    def __init__(self, api_key: str = None, model: str = "gpt-4.1", db: Session = None):
        """Initialize the ChatAgent with API key and model name."""
        # Use the provided API key or fall back to the one from settings
        api_key = api_key or settings.OPENAI_API_KEY
        logger.info(f'Using OpenAI API key from settings: {api_key[:5]}...' if api_key else 'No API key provided')
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self._function_mapping = None
        self.db = db
        
        # Load available functions from the tools wrapper
        self.available_functions = self._get_available_functions()
        
        # Initialize repository if db is provided
        self.conversation_repo = ConversationRepository(db) if db else None

    def _get_available_functions(self) -> List[Dict[str, Any]]:
        """Define the functions available to the model."""
        return Tools

    def _get_function_mapping(self) -> Dict[str, Callable]:
        """Get cached function mapping or create a new one."""
        if self._function_mapping is None:
            # Import only once when needed
            from .utils.tools_wrapper_util import (
                getSites,
                getProducts,
                getEmployees,
                AppointmentSuggestion_wrapper,
                bookAppointment,
                cancelAppointment,
                getProfile,
                getOrders,
                store_profile_wrapper,
            )
            
            self._function_mapping = {
                "getSites": getSites,
                "getProducts": getProducts,
                "getEmployees": getEmployees,
                "AppointmentSuggestion": AppointmentSuggestion_wrapper,
                "bookAppointment": bookAppointment,
                "cancelAppointment": cancelAppointment,
                "getProfile": getProfile,
                "getOrders": getOrders,
                "store_profile": store_profile_wrapper,
            }
        
        return self._function_mapping

    def handle_tool_calls(self, tool_calls: List[Any], user_id: str) -> List[Dict]:
        """Execute the specified functions and return the results."""
        logger.info(f"Handling {len(tool_calls)} tool calls for user {user_id}")
        
        function_mapping = self._get_function_mapping()
        results = []
        
        # Get business phone for this user if it's stored in the cache
        from app.utils.message_cache import MessageCache
        message_cache = MessageCache.get_instance()
        business_phone = message_cache.get_business_phone(user_id)
        if business_phone:
            logger.info(f"Found business phone number for user {user_id}: {business_phone}")
        
        for tool_call in tool_calls:
            # Handle different object formats
            try:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id
            except AttributeError as e:
                logger.error(f"Error accessing function attributes as object: {str(e)}")
                try:
                    # Try accessing attributes as dictionary
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    tool_call_id = tool_call["id"]
                except Exception as e2:
                    logger.error(f"Both object and dict access failed: {str(e2)}")
                    continue
            
            function_to_call = function_mapping.get(function_name)
            if not function_to_call:
                error_message = f"Function {function_name} not found"
                logger.error(error_message)
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "content": json.dumps({"error": error_message})
                })
                continue
            
            try:
                # Handle special cases for different functions
                if function_name == "bookAppointment":
                    # Add customerId if not provided
                    if "customerId" not in function_args:
                        function_args["customerId"] = user_id
                    
                    # Add business_phone_number if available
                    if business_phone and "business_phone_number" not in function_args:
                        logger.info(f"Adding business phone {business_phone} to bookAppointment call")
                        function_args["business_phone_number"] = business_phone
                        
                elif function_name == "cancelAppointment":
                    # Add mobileNumber if needed by the wrapper
                    function_args["mobileNumber"] = user_id
                elif function_name == "getProfile" or function_name == "getOrders":
                    # These functions have a mobile_number parameter
                    if not function_args:
                        function_args = {}
                    function_args["mobile_number"] = user_id
                    logger.info(f"Adding mobile_number={user_id} to {function_name} call")
                elif function_name == "store_profile":
                    # For store_profile, ensure mobile_number is set
                    if "mobile_number" not in function_args:
                        function_args["mobile_number"] = user_id
                
                # Debug logging
                logger.info(f"Calling function {function_name} with args: {function_args}")
                
                # Execute the function with proper error handling
                try:
                    function_response = function_to_call(**function_args)
                except TypeError as type_error:
                    # Handle parameter mismatches more gracefully
                    logger.error(f"TypeError in {function_name}: {str(type_error)}")
                    
                    # Special handling for common parameter errors
                    if function_name == "getProfile" and "mobile_number" in str(type_error):
                        # Try calling without parameters
                        logger.info("Retrying getProfile without any parameters")
                        function_response = getProfile()
                    elif function_name == "getOrders" and "mobile_number" in str(type_error):
                        # Try calling without parameters
                        logger.info("Retrying getOrders without any parameters")
                        function_response = getOrders()
                    else:
                        # If unsure how to fix, return error
                        raise
                
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "content": json.dumps(function_response)
                })
                
                logger.info(f"Successfully executed {function_name} for user {user_id}")
            except Exception as e:
                error_message = f"Error executing {function_name}: {str(e)}"
                logger.error(error_message)
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "content": json.dumps({"error": error_message})
                })
        
        return results

    def run_conversation(self, user_id: str, question: str) -> str:
        """Run a conversation using ChatCompletion API instead of Assistant API."""
        logger.info(f"Starting conversation for user {user_id}")
        
        # Add current date and time to the question for context
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question_with_time = f"{question}\n\n(Current Date and Time: {current_datetime})"
        
        # Retrieve conversation history from database or initialize if new
        try:
            conversation_history = self._get_conversation_history(user_id)
            if not conversation_history:
                logger.warning(f"No conversation history found for user {user_id}, using default")
                conversation_history = [{"role": "system", "content": System_prompt}]
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            conversation_history = [{"role": "system", "content": System_prompt}]
        
        # Set a reasonable timeout for the entire conversation
        timeout = 30  # 30 seconds max
        start_time = time.time()
        
        try:
            # Add user message to history
            conversation_history.append({"role": "user", "content": question_with_time})
            
            # Initial completion call with error handling
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation_history,
                    tools=self.available_functions,
                    tool_choice="auto",
                    temperature=0.25,
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"OpenAI API error: {error_str}")
                if "messages with role 'tool' must be a response to a preceeding message with 'tool_calls'" in error_str or "must be followed by tool messages responding to each 'tool_call_id'"  in error_str:
                    logger.warning("Detected tool_call mismatch error, clearing chat history and retrying once.")
                    # Clear chat history for this user
                    self._save_conversation_history(user_id, [{"role": "system", "content": System_prompt}])
                    # Retry once with only the system and user message
                    conversation_history = [{"role": "system", "content": System_prompt},
                                           {"role": "user", "content": question_with_time}]
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=conversation_history,
                            tools=self.available_functions,
                            tool_choice="auto",
                            temperature=0.25,
                        )
                    except Exception as api_error2:
                        logger.error(f"OpenAI API error after clearing history: {str(api_error2)}")
                        return f"Sorry, I couldn't process your request: {str(api_error2)}"
                else:
                    return f"Sorry, I couldn't process your request: {error_str}"
                
            # Process the response with safety checks
            if not response or not response.choices or len(response.choices) == 0:
                logger.error("Empty response from OpenAI API")
                return "Sorry, I received an empty response from the API. Please try again."
                
            response_message = response.choices[0].message
            
            # Process the response
            response_dict = {
                "role": response_message.role,
                "content": response_message.content if response_message.content is not None else "",
            }
            
            if response_message.tool_calls:
                # Debug print
                print(f"Tool calls in response: {response_message.tool_calls}")
                
                try:
                    tool_calls_for_storage = []
                    for tool in response_message.tool_calls:
                        tool_calls_for_storage.append({
                            "id": tool.id,
                            "type": tool.type,
                            "function": {
                                "name": tool.function.name,
                                "arguments": tool.function.arguments
                            }
                        })
                    response_dict["tool_calls"] = tool_calls_for_storage
                except Exception as e:
                    logger.error(f"Error processing tool calls for storage: {str(e)}")
                    # Fallback to a simpler representation
                    response_dict["tool_calls"] = [{"id": f"call_{i}", "type": "function", "function": {"name": "unknown", "arguments": "{}"}} 
                                                  for i, _ in enumerate(response_message.tool_calls)]
            
            conversation_history.append(response_dict)
            
            # Check if the model wants to call a function
            max_iterations = 10  # Prevent infinite loops
            iterations = 0
            
            while (
                response_message.tool_calls 
                and iterations < max_iterations 
                and (time.time() - start_time) < timeout
            ):
                iterations += 1
                logger.info(f"Processing tool calls, iteration {iterations}/{max_iterations}")
                
                # Execute the tool calls
                tool_results = self.handle_tool_calls(response_message.tool_calls, user_id)
                
                # Add tool results to conversation history
                conversation_history.extend(tool_results)
                
                # Clean the last tool messages before sending to OpenAI
                conversation_history = clean_last_tool_messages(conversation_history, window=5)
                
                # Get a new response from the model
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=conversation_history,
                        tools=self.available_functions,
                        tool_choice="auto",
                        temperature=0.2,
                    )
                except Exception as api_error:
                    error_str = str(api_error)
                    logger.error(f"OpenAI API error after tool calls: {error_str}")
                    if "must be followed by tool messages responding to each 'tool_call_id'" in error_str:
                        logger.warning("Detected tool_call mismatch error after tool calls, clearing chat history and retrying once.")
                        self._save_conversation_history(user_id, [{"role": "system", "content": System_prompt}])
                        conversation_history = [{"role": "system", "content": System_prompt},
                                               {"role": "user", "content": question_with_time}]
                        try:
                            response = self.client.chat.completions.create(
                                model=self.model,
                                messages=conversation_history,
                                tools=self.available_functions,
                                tool_choice="auto",
                                temperature=0.2,
                            )
                        except Exception as api_error2:
                            logger.error(f"OpenAI API error after clearing history: {str(api_error2)}")
                            return f"Sorry, I couldn't process your request: {str(api_error2)}"
                    else:
                        return f"Sorry, I couldn't process your request after executing functions: {error_str}"
                
                # Safety check for the response
                if not response or not response.choices or len(response.choices) == 0:
                    logger.error("Empty response from OpenAI API after tool calls")
                    return "Sorry, I received an empty response after processing your request. Please try again."
                
                # Process the new response
                response_message = response.choices[0].message
                
                # Convert the response_message to a dict for storage
                response_dict = {
                    "role": response_message.role,
                    "content": response_message.content if response_message.content is not None else "",
                }
                
                if response_message.tool_calls:
                    # Debug print
                    print(f"Tool calls in response: {response_message.tool_calls}")
                    
                    try:
                        tool_calls_for_storage = []
                        for tool in response_message.tool_calls:
                            tool_calls_for_storage.append({
                                "id": tool.id,
                                "type": tool.type,
                                "function": {
                                    "name": tool.function.name,
                                    "arguments": tool.function.arguments
                                }
                            })
                        response_dict["tool_calls"] = tool_calls_for_storage
                    except Exception as e:
                        logger.error(f"Error processing tool calls for storage: {str(e)}")
                        # Fallback to a simpler representation
                        response_dict["tool_calls"] = [{"id": f"call_{i}", "type": "function", "function": {"name": "unknown", "arguments": "{}"}} 
                                                      for i, _ in enumerate(response_message.tool_calls)]
                
                conversation_history.append(response_dict)
            
            # Save updated history (limit history to prevent token explosion)
            if conversation_history:
                try:
                    trimmed_history = self._trim_conversation_history(conversation_history)
                    if trimmed_history:
                        self._save_conversation_history(user_id, trimmed_history)
                    else:
                        logger.warning("Trimmed history is empty, not saving")
                except Exception as save_error:
                    logger.error(f"Error saving conversation history: {str(save_error)}")
            else:
                logger.warning(f"Not saving empty conversation history for user {user_id}")
            
            # Return the final text response with None handling
            return response_message.content or "I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error in run_conversation: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _get_conversation_history(self, user_id: str) -> List[Dict]:
        """
        Retrieve conversation history for a user from database.
        If not found, return a default system message.
        """
        # System message to include regardless of history
        system_message = {
            "role": "system", 
            "content": System_prompt
        }
        
        # If we have no repository or db connection, just return the system message
        if not self.conversation_repo or not self.db:
            return [system_message]
        
        # Try to get history from repository
        try:
            history = self.conversation_repo.get_conversation_history(user_id)
            if history and len(history) > 0:
                # Ensure the system message is at the beginning
                if history[0].get("role") != "system":
                    history.insert(0, system_message)
                return history
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
        
        # Return default if repository failed or no history found
        return [system_message]
    
    def _save_conversation_history(self, user_id: str, history: List[Dict]) -> None:
        """Save conversation history for a user to database."""
        if not self.conversation_repo or not self.db:
            return
        
        try:
            self.conversation_repo.save_conversation_history(user_id, history)
        except Exception as e:
            logger.error(f"Error saving conversation history: {str(e)}")
    
    def _trim_conversation_history(self, history: List[Dict], max_tokens: int = 4000) -> List[Dict]:
        """
        Trim conversation history to prevent token limits.
        Keep the system message, and most recent messages within token limit.
        """
        if not history:
            return []
        
        # Always keep the system message
        system_message = None
        if history and len(history) > 0 and history[0].get("role") == "system":
            system_message = history[0]
            history = history[1:]
        
        # Simple token estimation (rough approximation)
        def estimate_tokens(message: Dict) -> int:
            content = message.get("content", "")
            # Handle None content
            if content is None:
                content = ""
            # Rough estimate: 1 token per 4 characters + 3 for message metadata
            return len(content) // 4 + 3
        
        # Keep most recent messages within token limit
        total_tokens = 0
        trimmed_history = []
        
        # Process messages in reverse (newest first)
        for message in reversed(history):
            message_tokens = estimate_tokens(message)
            if total_tokens + message_tokens <= max_tokens:
                trimmed_history.insert(0, message)
                total_tokens += message_tokens
            else:
                break
        
        # Add back the system message
        if system_message:
            trimmed_history.insert(0, system_message)
        
        return trimmed_history 