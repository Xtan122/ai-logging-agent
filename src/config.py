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

    LLM provider is selected via LLM_PROVIDER env var ('gemini' or 'github').
    AWS and Slack credentials are optional — tools fall back to placeholder
    mode when they are not configured.
    """

    # ── LLM Provider ──────────────────────────────────────────────────────────
    # 'gemini' (default) or 'github'
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()

    # ── Gemini ────────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # ── GitHub Models ─────────────────────────────────────────────────────────
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODEL: str = os.getenv("GITHUB_MODEL", "openai/gpt-4.1")
    GITHUB_ENDPOINT: str = os.getenv(
        "GITHUB_ENDPOINT",
        "https://models.github.ai/inference",
    )

    # ── AWS ───────────────────────────────────────────────────────────────────
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_RDS_INSTANCE_ID: str = os.getenv("AWS_RDS_INSTANCE_ID", "")

    # ── Slack ─────────────────────────────────────────────────────────────────
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_CHANNEL: str = os.getenv("SLACK_CHANNEL", "#devops-alerts")

    # ── Paths ─────────────────────────────────────────────────────────────────
    LOG_DIRECTORY: str = os.getenv("LOG_DIRECTORY", "logs")

    # ── Agent ─────────────────────────────────────────────────────────────────
    MAX_ITERATIONS: int = 10
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    VERBOSE: bool = True

    # Backward-compat alias (old typo kept so nothing breaks while migrating)
    MAX_INTERATIONS: int = MAX_ITERATIONS

    @classmethod
    def validate(cls) -> None:
        """
        Validate that the selected LLM provider has the required credentials.
        AWS and Slack are optional; missing credentials just enable placeholder mode.

        Raises:
            ValueError: if the active provider is missing its API key/token.
        """
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError(
                "LLM_PROVIDER=gemini but GEMINI_API_KEY is not set."
            )
        if cls.LLM_PROVIDER == "github" and not cls.GITHUB_TOKEN:
            raise ValueError(
                "LLM_PROVIDER=github but GITHUB_TOKEN is not set."
            )

    @classmethod
    def get_system_prompt(cls) -> str:
        """
        Load the system prompt from system_prompt.txt (required) and append
        examples.txt (optional) if it exists.

        Returns:
            str: The full system prompt string.
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))

        with open(os.path.join(base_dir, "system_prompt.txt"), "r", encoding="utf-8") as f:
            prompt = f.read()

        examples_file = os.path.join(base_dir, "examples.txt")
        try:
            with open(examples_file, "r", encoding="utf-8") as f:
                prompt += "\n\n" + f.read()
        except FileNotFoundError:
            pass  # examples are optional

        return prompt
