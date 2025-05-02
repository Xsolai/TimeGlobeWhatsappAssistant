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
        
    def is_processed(self, message_id):
        """Check if a message ID has already been processed"""
        if not message_id:
            return False
        return message_id in self.processed_messages
        
    def mark_as_processed(self, message_id):
        """Mark a message ID as processed"""
        if not message_id:
            return
            
        import time
        self.processed_messages[message_id] = time.time()
        
        # Simple cache cleanup - if we exceed max size, remove oldest entries
        if len(self.processed_messages) > self.max_cache_size:
            # Sort by timestamp and keep only the newest entries
            sorted_items = sorted(self.processed_messages.items(), 
                                 key=lambda x: x[1], reverse=True)
            # Keep only the newest max_cache_size/2 entries
            keep_count = self.max_cache_size // 2
            self.processed_messages = dict(sorted_items[:keep_count]) 
            
    def set_business_phone(self, user_number, business_phone):
        """Store the business phone number for a user"""
        if not user_number or not business_phone:
            return False
        
        import logging
        logging.info(f"Storing business phone {business_phone} for user {user_number}")
        self.business_phones[user_number] = business_phone
        return True
        
    def get_business_phone(self, user_number):
        """Get the stored business phone number for a user"""
        if not user_number:
            return None
            
        return self.business_phones.get(user_number) 