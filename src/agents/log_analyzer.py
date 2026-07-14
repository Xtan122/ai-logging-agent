from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..models import GeminiModel
from ..tools import get_log_tools, requires_approval
from ..utils.response import extract_response_text
from ..config import Config

CONFIRMATIONS = {'yes', 'y', 'true', '1', 'ok', 'affirmative', 'confirm', 'sure', 'correct'}

def if_confirm(text: str) -> bool:
    return text.strip().lower() in CONFIRMATIONS

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

        # No internal history — caller (Streamlit) owns conversation state

        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", Config.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create chain
        self.chain = self.prompt | self.llm_with_tools

    def process_query(
        self,
        user_input: str,
        chat_history: list = None,
        approval_granted: bool = False,
    ):
        """
        Process a user query and return the response.

        Returns either:
        - str  : the agent's final text response, OR
        - dict : {"blocked": True, "tool_call": ..., "message": ...}
                 when a destructive tool needs user confirmation (Turn 1).

        Approval flow (matches the sequence diagram):
          Turn 1 ─ LLM calls a gated tool → agent returns blocked sentinel.
          Turn 2 ─ User says "yes", caller sets approval_granted=True and
                    re-invokes.  LLM re-emits the tool call; gate is open.

        Args:
            user_input (str): The user's message.
            chat_history (list): Full prior conversation history.
            approval_granted (bool): Set True when the user has confirmed
                a previously blocked action.

        Returns:
            str | dict
        """
        if chat_history is None:
            chat_history = []

        try:
            response = self.chain.invoke({
                "chat_history": chat_history,
                "input": user_input,
            })

            if getattr(response, "tool_calls", None):
                tool_messages = [HumanMessage(content=user_input)]
                response = self.handle_tool_call(
                    tool_messages,
                    response,
                    chat_history,
                    approval_granted=approval_granted,
                )

            # Blocked sentinel — pass straight through to caller
            if isinstance(response, dict) and response.get("blocked"):
                return response

            return extract_response_text(response)

        except Exception as e:
            error_message = f"Error: An unexpected error occurred while processing the query: {str(e)}"
            print(error_message)
            import traceback
            traceback.print_exc()
            return error_message

    def processing_query(
        self,
        user_input: str,
        chat_history: list = None,
        approval_granted: bool = False,
    ) -> str:
        return self.process_query(user_input, chat_history, approval_granted)

    def _invoke_with_history(self, extra_messages: list, chat_history: list):
        """
        Invoke the LLM during tool-call iterations.

        `extra_messages` contains the current turn's thread:
        HumanMessage → AIMessage(tool_calls) → ToolMessage(s) …
        Prepend the caller-supplied chat_history so the model retains prior context.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", Config.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
        ])
        chain = prompt | self.llm_with_tools
        return chain.invoke({
            "chat_history": chat_history + extra_messages,
        })

    def handle_tool_call(
        self,
        messages: list,
        response,
        chat_history: list,
        approval_granted: bool = False,
    ):
        """
        Execute tool calls from the LLM, with a human-in-the-loop gate for
        destructive tools.

        Approval flow (two-turn pattern from the sequence diagram):

        Turn 1 ─ approval_granted=False (default)
          • LLM emits tool_call for a gated tool.
          • Agent injects a BLOCKED ToolMessage so the LLM knows it was stopped.
          • LLM writes a recommendation / evidence summary.
          • Agent returns sentinel: {"blocked": True, "tool_call": ..., "message": ...}
          • Caller displays the recommendation and waits for the user.

        Turn 2 ─ approval_granted=True  (caller detected user said "yes")
          • Chat history now includes the recommendation from Turn 1.
          • LLM sees the context and re-emits the same tool_call.
          • Gate checks requires_approval() → True, but approval_granted=True → allowed.
          • Tool executes; result returned normally.

        Args:
            messages:         Current-turn message thread (mutated in place).
            response:         Latest AIMessage from the LLM.
            chat_history:     Full prior conversation history.
            approval_granted: True when the user has already confirmed the action.
        """
        tool_map = {tool.name: tool for tool in self.tools}
        current_response = response
        max_iterations = Config.MAX_INTERATIONS

        for _ in range(max_iterations):
            tool_calls = getattr(current_response, "tool_calls", None) or []
            if not tool_calls:
                return current_response

            messages.append(current_response)

            for tool_call in tool_calls:
                tool_name    = tool_call.get("name")
                tool_args    = tool_call.get("args", {})
                tool_call_id = tool_call.get("id")
                tool_func    = tool_map.get(tool_name)

                # ── APPROVAL GATE ───────────────────────────────────────────
                if requires_approval(tool_name):
                    if not approval_granted:
                        # --- BLOCKED: inject hint so LLM writes a recommendation
                        block_hint = ToolMessage(
                            content=(
                                f"[BLOCKED] Tool '{tool_name}' requires user approval "
                                f"before execution.\nArguments: {tool_args}\n"
                                "Summarise your findings and ask the user to confirm."
                            ),
                            tool_call_id=tool_call_id or tool_name,
                        )
                        messages.append(block_hint)
                        recommendation = self._invoke_with_history(messages, chat_history)
                        return {
                            "blocked": True,
                            "tool_call": tool_call,
                            "message": extract_response_text(recommendation),
                        }
                    # --- ALLOWED: approval_granted=True, fall through to execute

                # ── Execute tool (safe or approved) ───────────────────────────
                if tool_func is None:
                    tool_result = f"Error: Tool '{tool_name}' is not available."
                else:
                    try:
                        tool_result = tool_func.invoke(tool_args)
                    except Exception as e:
                        tool_result = f"Error: {str(e)}"

                messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call_id or tool_name,
                    )
                )

            current_response = self._invoke_with_history(messages, chat_history)

        raise RuntimeError("Exceeded maximum tool iterations while processing the query.")
