import unittest
from app.core.config import settings
from app.services.dialog360_service import Dialog360Service

class TestDialog360(unittest.TestCase):
    def setUp(self):
        self.service = Dialog360Service(
            api_key=settings.DIALOG360_API_KEY,
            api_url=settings.DIALOG360_API_URL,
            phone_number=settings.DIALOG360_PHONE_NUMBER
        )

    def test_send_message(self):
        # Test sending a message
        response = self.service.send_message("+1234567890", "Test message")
        self.assertIsNotNone(response)
        # Add more specific assertions based on your requirements

if __name__ == '__main__':
    unittest.main() 