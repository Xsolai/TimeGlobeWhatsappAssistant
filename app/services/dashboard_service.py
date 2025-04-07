from ..core.config import settings
import requests, time, json
from fastapi import HTTPException, status
from ..repositories.dashboard_repository import DashboardRepository
from ..db.session import get_db
from ..logger import main_logger
from sqlalchemy.orm import Session
from datetime import datetime
import re


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DashboardRepository(db)

    def overview(self, user_id: int):
        try:
            main_logger.info(f"Fetching Dashboard Overview")
            main_logger.info(f"Appointment Fetched")
            return self.repo.overview(user_id=user_id)
        except Exception as e:
            main_logger.error(f"Error fetching Overview : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_appointment(self, range: str, userd_id: int):
        try:
            main_logger.info(f"Fetching Appointments")
            days_mapping = {"7d": 7, "30d": 30, "90d": 90}
            day = days_mapping.get(range)
            main_logger.info(f"Appointment Fetched")
            return self.repo.get_appointments(days=day, user_id=userd_id)
        except Exception as e:
            main_logger.error(f"Error fetching appointments : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_top_services(self, user_id: int):
        try:
            main_logger.info(f"Fetching top services for user_id: {user_id}")
            return self.repo.get_top_service(user_id=user_id)
        except Exception as e:
            main_logger.error(f"Error fetching top services : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_top_customers(self, user_id: int):
        try:
            main_logger.info(f"Fetch Top Customer for user_id: {user_id}")
            return self.repo.get_top_customer(user_id)
        except Exception as e:
            main_logger.error(f"Error fetching top Customer : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_ai_logs(self, limit: int = 10):
        try:
            main_logger.info(f"Fetching Ai Logs with limit {limit}")
            logs = []
            with open("app.log", "r") as file:
                for line in file:
                    # Look specifically for the JSON format in app INFO logs
                    if " - app - INFO - {" in line:
                        try:
                            # Extract the part that contains the JSON
                            json_str = line.split(" - app - INFO - ", 1)[1].strip()
                            # Parse the JSON data
                            log_data = json.loads(json_str)
                            # Remove 'receiver' if present
                            log_data.pop("receiver", None)
                            # Add timestamp from log if not in JSON
                            if "timestamp" not in log_data:
                                log_timestamp = line.split(",")[0]
                                log_data["log_timestamp"] = log_timestamp
                            logs.append(log_data)
                        except (json.JSONDecodeError, IndexError) as e:
                            # Skip lines with invalid JSON or incorrect format
                            continue
            # Return the last 'limit' logs
            return logs[-limit:] if logs else []
        except Exception as e:
            main_logger.error(f"Error Fetch Ai logs {e}")
            raise HTTPException(
                status_code=500,
                detail="There is internal error for processing your request.",
            )

    def get_ai_perfomance(self, user_id: int):
        try:
            main_logger.info(f"Fetching ai performance for user_id: {user_id}")
            response_time = self.calculate_average_response_time_from_log()
            result = self.repo.ai_performance(user_id=user_id)
            total_interaction = self.get_total_interaction_count()
            result["average_response_time"] = response_time
            result["total_interactions"] = total_interaction
            return result
        except Exception as e:
            main_logger.error(f"Error fetching ai performance : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_total_interaction_count(self):
        try:
            main_logger.info("Fetching Ai Logs count")
            logs_count = 0  # Initialize count

            with open("app.log", "r") as file:
                for line in file:
                    # Look specifically for the JSON format in app INFO logs
                    if " - app - INFO - {" in line:
                        try:
                            # Extract the part that contains the JSON
                            json_str = line.split(" - app - INFO - ", 1)[1].strip()
                            # Parse the JSON data
                            json.loads(
                                json_str
                            )  # Just parse the JSON to check if it's valid
                            logs_count += 1  # Increment the count for each valid log
                        except (json.JSONDecodeError, IndexError) as e:
                            # Skip lines with invalid JSON or incorrect format
                            continue

            # Return the total count of logs found
            return logs_count

        except Exception as e:
            main_logger.error(f"Error Fetching Ai logs count: {e}")
            raise HTTPException(
                status_code=500,
                detail="There is an internal error while processing your request.",
            )

    def calculate_average_response_time_from_log(self):
        try:
            response_times = []

            # Regular expression to match lines starting with 'get_response_from_gpt()' and extract the time (e.g., "completed in 15.42s")
            pattern = re.compile(r"get_response_from_gpt\(\).*completed in (\d+\.\d+)s")

            # Open and read the log file
            with open("app.log", "r") as file:
                for line in file:
                    # Search for lines that start with 'get_response_from_gpt()' and match the time pattern
                    match = pattern.search(line)
                    if match:
                        # Extract the time duration from the match
                        duration = float(match.group(1))
                        response_times.append(duration)

            # If there are no response times found
            if not response_times:
                return "No response times found."

            # Calculate the average response time
            avg_response_time = sum(response_times) / len(response_times)
            return f"{round(avg_response_time, 2)}s"

        except Exception as e:
            print(f"Error calculating average response time: {e}")
            return "Error"
