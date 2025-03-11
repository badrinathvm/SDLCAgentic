from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv

class GroqLLM:
    def __init__(self):
        load_dotenv()

    def get_llm(self):
        try: 
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            llm = ChatGroq(api_key=self.groq_api_key, model='qwen-2.5-32b')
            return llm
        except Exception as e:
            raise ValueError(f"Error occurred with exception: {e}")