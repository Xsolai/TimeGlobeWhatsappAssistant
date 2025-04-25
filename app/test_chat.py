import os
from dotenv import load_dotenv
import time
from chat_agent import ChatAgent
from sqlalchemy.orm import Session
from db.session import SessionLocal

load_dotenv()

def test_chat_agent():
    """Test the ChatAgent implementation with a simple conversation"""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
    
    # Create a database session
    db = SessionLocal()
    
    # Create the chat agent
    chat_agent = ChatAgent(api_key=api_key, model="gpt-4o", db=db)
    
    # Test phone number (for demo purposes)
    test_user = "1234567890"
    
    # Test conversation
    questions = [
        "Welche Dienstleistungen bietet ihr an?",
        "Ich möchte einen Haarschnitt buchen. Welche Salons gibt es?",
        "Gibt es freie Termine für nächste Woche?"
    ]
    
    for question in questions:
        print(f"\nUser: {question}")
        start_time = time.time()
        
        # Get response
        response = chat_agent.run_conversation(test_user, question)
        
        end_time = time.time()
        print(f"Assistant: {response}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Clean up
    db.close()

if __name__ == "__main__":
    test_chat_agent() 