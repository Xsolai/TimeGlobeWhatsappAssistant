class MessageCache:
    """
    Simple in-memory cache to prevent duplicate processing of the same message ID.
    Uses a singleton pattern to maintain a single cache across requests.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MessageCache()
        return cls._instance
    
    def __init__(self):
        # Store processed message IDs with a timestamp
        # Using a dict instead of a set to potentially expire old entries
        self.processed_messages = {}
        # Store business phone numbers per user
        self.business_phones = {}
        # Maximum cache size to prevent memory issues
        self.max_cache_size = 1000
        # Import standard modules
        import time
        import logging
        self.time = time
        self.logger = logging
        self.logger.info("MessageCache initialized")
        
    def is_processed(self, message_id):
        """Check if a message ID has already been processed"""
        if not message_id:
            self.logger.warning("Empty message_id passed to is_processed")
            return False
            
        # Check if message ID exists in the cache
        is_present = message_id in self.processed_messages
        
        if is_present:
            process_time = self.processed_messages[message_id]
            current_time = self.time.time()
            elapsed_time = current_time - process_time
            self.logger.warning(f"Duplicate message detected - ID: {message_id}, first seen {elapsed_time:.2f} seconds ago")
        
        return is_present
        
    def mark_as_processed(self, message_id):
        """Mark a message ID as processed"""
        if not message_id:
            self.logger.warning("Empty message_id passed to mark_as_processed")
            return
         
        # Always mark as processed, even if already exists (updates timestamp)
        current_time = self.time.time()
        self.processed_messages[message_id] = current_time
        self.logger.info(f"Message marked as processed: {message_id} at timestamp {current_time}")
        
        # Simple cache cleanup - if we exceed max size, remove oldest entries
        if len(self.processed_messages) > self.max_cache_size:
            # Sort by timestamp and keep only the newest entries
            sorted_items = sorted(self.processed_messages.items(), 
                                 key=lambda x: x[1], reverse=True)
            # Keep only the newest max_cache_size/2 entries
            keep_count = self.max_cache_size // 2
            self.processed_messages = dict(sorted_items[:keep_count])
            self.logger.info(f"Cache cleanup performed. Kept {keep_count} entries, removed {len(sorted_items) - keep_count}")
            
    def set_business_phone(self, user_number, business_phone):
        """Store the business phone number for a user"""
        if not user_number or not business_phone:
            self.logger.warning(f"Invalid parameters for set_business_phone: user={user_number}, phone={business_phone}")
            return False
        
        self.logger.info(f"Storing business phone {business_phone} for user {user_number}")
        self.business_phones[user_number] = business_phone
        return True
        
    def get_business_phone(self, user_number):
        """Get the stored business phone number for a user"""
        if not user_number:
            self.logger.warning("Empty user_number passed to get_business_phone")
            return None
        
        business_phone = self.business_phones.get(user_number)
        if not business_phone:
            self.logger.info(f"No business phone found for user {user_number}")
        else:
            self.logger.debug(f"Retrieved business phone {business_phone} for user {user_number}")
            
        return business_phone 