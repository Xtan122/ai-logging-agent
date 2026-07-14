from ..config import Config


def create_model():
    """
    Instantiate the correct LLM wrapper based on Config.LLM_PROVIDER.

    Supported providers:
        'gemini'  → GeminiModel  (default)
        'github'  → GitHubModel

    Raises:
        ValueError: if LLM_PROVIDER is set to an unrecognised value.
    """
    provider = Config.LLM_PROVIDER

    if provider == "gemini":
        from .gemini import GeminiModel
        return GeminiModel()

    elif provider == "github":
        from .github_openai import GitHubModel
        return GitHubModel()

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{provider}'. "
            "Choose 'gemini' or 'github'."
        )