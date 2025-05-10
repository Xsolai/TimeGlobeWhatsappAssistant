import queue
import threading
import time
import logging
import traceback
import asyncio
from typing import Dict, Any, Callable
from ..db.session import SessionLocal
from ..services.dialog360_service import Dialog360Service

# Configure logging
logger = logging.getLogger(__name__)

class MessageQueue:
    """
    A message queue implementation using Python's Queue and threading.
    Uses a singleton pattern to maintain a single queue across the application.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MessageQueue()
        return cls._instance
    
    def __init__(self):
        # Create queue for incoming messages
        self.message_queue = queue.Queue()
        
        # Flag to control worker threads
        self.running = False
        
        # Worker threads
        self.worker_threads = []
        
        # Number of worker threads to spawn
        self.num_workers = 3
        
        # Message processor function
        self.message_processor = None
        
        logger.info("MessageQueue initialized")
    
    def enqueue_message(self, message_data: Dict[str, Any]):
        """Add a message to the processing queue"""
        try:
            self.message_queue.put(message_data)
            logger.info(f"Message enqueued. Queue size: {self.message_queue.qsize()}")
            return True
        except Exception as e:
            logger.error(f"Error enqueueing message: {str(e)}")
            return False
    
    def start_workers(self, message_processor: Callable):
        """Start worker threads to process messages from the queue"""
        if self.running:
            logger.warning("Workers already running")
            return
        
        self.running = True
        self.message_processor = message_processor
        
        # Create and start worker threads
        for i in range(self.num_workers):
            thread = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True  # Make threads daemon so they exit when main thread exits
            )
            self.worker_threads.append(thread)
            thread.start()
            logger.info(f"Started worker thread {i}")
    
    def stop_workers(self):
        """Stop all worker threads"""
        self.running = False
        
        # Wait for all threads to finish
        for i, thread in enumerate(self.worker_threads):
            if thread.is_alive():
                logger.info(f"Waiting for worker thread {i} to finish...")
                thread.join(timeout=5)  # Give each thread 5 seconds to finish
        
        self.worker_threads = []
        logger.info("All worker threads stopped")
    
    def _worker_loop(self, worker_id: int):
        """Worker thread loop to process messages from the queue"""
        logger.info(f"Worker {worker_id} started")
        
        # Create an event loop for this thread to handle async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.running:
            try:
                # Get message with timeout to allow for worker stopping
                try:
                    message_data = self.message_queue.get(timeout=1)
                except queue.Empty:
                    # No message in queue, continue loop
                    continue
                
                # Log message receipt
                logger.info(f"Worker {worker_id} processing message")
                
                # Create database session
                db = SessionLocal()
                try:
                    # Process the message
                    dialog360_service = Dialog360Service(db)
                    
                    # Check if processor is async or sync and call appropriately
                    if asyncio.iscoroutinefunction(self.message_processor):
                        # Run async function in the thread's event loop
                        loop.run_until_complete(
                            self.message_processor(message_data, dialog360_service)
                        )
                    else:
                        # Run synchronous function directly
                        self.message_processor(message_data, dialog360_service)
                    
                    # Mark task as done
                    self.message_queue.task_done()
                    logger.info(f"Worker {worker_id} completed message processing")
                    
                except Exception as e:
                    # Log the exception
                    logger.error(f"Worker {worker_id} error processing message: {str(e)}")
                    logger.error(traceback.format_exc())
                    
                    # Still mark task as done even if it failed
                    self.message_queue.task_done()
                finally:
                    # Always close the database session
                    db.close()
                
            except Exception as e:
                # Log any other exceptions in the worker loop
                logger.error(f"Worker {worker_id} loop error: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Brief sleep to prevent CPU spinning on repeated errors
                time.sleep(0.5)
        
        # Close the event loop when thread is stopping
        loop.close()
        logger.info(f"Worker {worker_id} stopped")

def clean_last_tool_message(history):
    # Only check the last two messages
    if len(history) >= 1 and history[-1]['role'] == 'tool':
        if len(history) == 1 or history[-2]['role'] != 'tool_calls':
            history.pop()
    return history 