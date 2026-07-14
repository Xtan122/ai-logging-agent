from langchain_openai import ChatOpenAI
from ..config import Config


class GitHubModel:
    """LLM wrapper for GitHub Models (OpenAI-compatible endpoint)."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.GITHUB_MODEL,
            api_key=Config.GITHUB_TOKEN,
            base_url=Config.GITHUB_ENDPOINT,
            temperature=Config.TEMPERATURE,
        )

    def get_llm(self):
        return self.llm

    def get_llm_with_tools(self, tools: list):
        return self.llm.bind_tools(tools)