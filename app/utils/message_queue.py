import queue
import threading
import time
import logging
import traceback
import asyncio
from typing import Dict, Any, Callable
from ..db.session import SessionLocal
from ..services.dialog360_service import Dialog360Service
from ..services.whatsapp_business_service import WhatsAppBusinessService

# Configure logging
logger = logging.getLogger(__name__)

class MessageQueue:
    """
    A message queue implementation using Python's Queue and threading.
    Uses a singleton pattern to maintain a single queue across the application.
    Supports both Dialog360 and WhatsApp Business API services.
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
        
        logger.info("MessageQueue initialized with dual service support")
    
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
    
    def _determine_service_type(self, message_data: Dict[str, Any]) -> str:
        """
        Determine which service to use based on the message format.
        Returns 'whatsapp_business' for new format, 'dialog360' for legacy format.
        """
        if message_data.get('object') == 'whatsapp_business_account':
            return 'whatsapp_business'
        elif 'entry' in message_data and message_data.get('entry', [{}])[0].get('changes'):
            # Could be Dialog360 format
            return 'dialog360'
        else:
            # Default to WhatsApp Business API for unknown formats
            return 'whatsapp_business'
    
    def _worker_loop(self, worker_id: int):
        """Worker thread loop to process messages from the queue"""
        logger.info(f"Worker {worker_id} started with dual service support")
        
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
                    # Determine which service to use
                    service_type = self._determine_service_type(message_data)
                    logger.info(f"Worker {worker_id} using {service_type} service")
                    
                    # Create the appropriate service
                    if service_type == 'whatsapp_business':
                        service = WhatsAppBusinessService(db)
                        logger.info(f"Worker {worker_id} created WhatsApp Business API service")
                    else:
                        service = Dialog360Service(db)
                        logger.info(f"Worker {worker_id} created Dialog360 service (DEPRECATED)")
                    
                    # Check if processor is async or sync and call appropriately
                    if asyncio.iscoroutinefunction(self.message_processor):
                        # Run async function in the thread's event loop
                        loop.run_until_complete(
                            self.message_processor(message_data, service)
                        )
                    else:
                        # Run synchronous function directly
                        self.message_processor(message_data, service)
                    
                    # Mark task as done
                    self.message_queue.task_done()
                    logger.info(f"Worker {worker_id} completed message processing using {service_type} service")
                    
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

def clean_last_tool_messages(history, window=5):
    """
    Check the last `window` messages and remove any 'tool' message
    that is not immediately after a 'tool_calls' message.
    """
    start = max(0, len(history) - window)
    i = start
    while i < len(history):
        if history[i]['role'] == 'tool':
            if i == 0 or history[i-1]['role'] != 'tool_calls':
                history.pop(i)
                # After popping, don't increment i, as the next item shifts into this index
                continue
        i += 1
    return history 