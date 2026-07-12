from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from ..models import GeminiModel
from ..tools import get_log_tools
from ..utils.response import extract_response_text
from ..config import Config

class LogAnalyzerAgent:
    """
    AI Logging Agent

    Capabilities:
    - Read and analyze log files
    - Answer questions about logs
    - Maintain conversation history

    Limitations:
    - No routing decisions
    - No automated actions
    - No multi-source integration
    """

    def __init__(self):
        """
        Initialize the agent
        """

        # Initialize the model
        self.model = GeminiModel()
        self.llm = self.model.get_llm()

        # Get tools
        self.tools = get_log_tools()

        # Bind tools to the model
        self.llm_with_tools = self.model.get_llm_with_tools(self.tools)

        # Chat memory
        self.chat_history = InMemoryChatMessageHistory()

        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", Config.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create chain
        self.chain = self.prompt | self.llm_with_tools

    def process_query(self, user_input: str) -> str:
        """
        Process a user query and return the response.

        Args:
            user_input (str): The user's input query.

        Returns:
            str: The response from the AI agent.
        """
        try:
            # First call: use the main chain with proper prompt template
            response = self.chain.invoke({
                "chat_history": self.chat_history.messages,
                "input": user_input,
            })

            if getattr(response, "tool_calls", None):
                # Pass only tool-resolution messages (not the full history)
                tool_messages = [HumanMessage(content=user_input)]
                response = self.handle_tool_call(tool_messages, response)

            response_text = extract_response_text(response)

            # Persist to history AFTER a successful round-trip (only if non-empty)
            if response_text:
                self.chat_history.add_message(HumanMessage(content=user_input))
                self.chat_history.add_message(AIMessage(content=response_text))

            return response_text

        except Exception as e:
            error_message = f"Error: An unexpected error occurred while processing the query: {str(e)}"
            print(error_message)
            import traceback
            traceback.print_exc()
            return error_message

    def processing_query(self, user_input: str) -> str:
        return self.process_query(user_input)

    def _invoke_with_history(self, extra_messages: list):
        """
        Invoke the LLM during tool-call iterations.

        During tool resolution we already have the full message thread in
        `extra_messages` (HumanMessage → AIMessage with tool_calls → ToolMessages …).
        We prepend the persisted chat history so the model retains earlier context,
        then send the whole sequence as a flat message list.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", Config.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
        ])
        chain = prompt | self.llm_with_tools
        return chain.invoke({
            "chat_history": self.chat_history.messages + extra_messages,
        })

    def handle_tool_call(self, messages, response) -> str:
        """
        Handle the tool call from the model and return the final response.

        Args:
            tool_call: The tool call object from the model.
            user_input (str): The user's input query.

        """
        tool_map = {tool.name: tool for tool in self.tools}
        current_response = response
        max_iterations = Config.MAX_INTERATIONS

        for _ in range(max_iterations):
            tool_calls = getattr(current_response, "tool_calls", None) or []
            if not tool_calls:
                return current_response

            messages.append(current_response)

            resolved_tool_messages = []
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_call_id = tool_call.get("id")
                tool_func = tool_map.get(tool_name)

                if tool_func is None:
                    tool_result = f"Error: Tool '{tool_name}' is not available."
                else:
                    try:
                        tool_result = tool_func.invoke(tool_args)
                    except Exception as e:
                        tool_result = f"Error: {str(e)}"

                tool_message = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call_id or tool_name,
                )
                resolved_tool_messages.append(tool_message)
                messages.append(tool_message)

            current_response = self._invoke_with_history(messages)

        raise RuntimeError("Exceeded maximum tool iterations while processing the query.")
