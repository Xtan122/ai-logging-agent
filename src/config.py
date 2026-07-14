"""
Configurations for the AI Log Analyzer.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the AI Log Analyzer.
    """

    # API Congiguration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.1))

    # Paths
    LOG_DIRECTORY: str = os.getenv("LOG_DIRECTORY", "logs")

    # Agent configuration
    MAX_INTERATIONS: int = 5
    VERBOSE: bool = True

    @classmethod
    def validate(cls):
        """
        Validates the configuration values.
        Raises ValueError if any required configuration is missing or invalid.
        """
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        if not os.path.isdir(cls.LOG_DIRECTORY):
            raise ValueError(f"LOG_DIRECTORY '{cls.LOG_DIRECTORY}' does not exist.")

    @classmethod
    def get_system_prompt(cls) -> str:
        """
        Returns the system prompt for the AI Log Analyzer.
        """
        # system_prompt.txt lives in the project root (one level above src/)
        prompt_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "system_prompt.txt")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()


            

