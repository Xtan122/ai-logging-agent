"""
Google Gemini wrapper
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config import Config

class GeminiModel:
    """
    Wrapper for Gemini model
    """

    def __init__(self):
        """
        Initializes the Gemini model with the specified configuration.
        """
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            google_api_key=Config.GEMINI_API_KEY,
            temperature=Config.TEMPERATURE
        )

    def get_llm(self):
        """
        Returns the Gemini model instance.
        """
        return self.llm
    
    def get_llm_with_tools(self, tools):
        """
        Returns the Gemini model instance bound with the specified tools.
        """
        return self.llm.bind_tools(tools)