#!/usr/bin/env python3
"""
AI Logging Agent
Main entry point for the interactive agent
"""
import sys
from langchain_core.messages import HumanMessage, AIMessage
from .agents import LogAnalyzerAgent
from .agents.log_analyzer import if_confirm
from .config import Config
from .utils.response import extract_response_text

def print_banner():
    print("====================================")
    print("      AI Log Analyzer Agent         ")
    print("====================================")
    print("\nCapacities:")
    print("- Analyze log files for patterns and anomalies")
    print("- Classify severity (P1/P2/P3/Info) and recommend actions")
    print("- Execute remediation actions (e.g., restart pod) with your approval")
    print("\nCommand:")
    print("Type your query and press Enter. Type 'exit' or 'quit' to terminate the session.")
    print("Type 'clear' to clear the chat history.\n")
    print("Type 'help' to see this message again.\n")
    print("="* 50 + "\n")

def main():
    try:
        Config.validate()

        print_banner()

        agent = LogAnalyzerAgent()

        # main.py owns the conversation history.
        # It is passed to the stateless agent on every call.
        chat_history: list = []

        # Holds the blocked sentinel between turns while we wait for the user's
        # confirmation.  None means no action is pending.
        pending_blocked: dict | None = None

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue  # Skip empty input

                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting AI Log Analyzer. Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    chat_history.clear()
                    pending_blocked = None
                    print("Chat history cleared.")
                    continue
                elif user_input.lower() == 'help':
                    print_banner()
                    continue

                # ── Turn 2: user is responding to a pending approval ──────────
                if pending_blocked is not None:
                    tool_name = pending_blocked["tool_call"].get("name", "unknown tool")

                    if if_confirm(user_input):
                        # approval_granted=True → gate opens, LLM re-emits tool call
                        print(f"✅ Approved. Executing {tool_name}...")
                        result = agent.process_query(
                            user_input,
                            chat_history,
                            approval_granted=True,
                        )
                        pending_blocked = None
                    else:
                        print(f"❌ Cancelled. '{tool_name}' was NOT executed.")
                        result = "Understood, the action has been cancelled."
                        pending_blocked = None

                # ── Turn 1 (or any normal turn) ───────────────────────────────
                else:
                    print("Processing your query...")
                    result = agent.process_query(user_input, chat_history)

                # ── Blocked sentinel returned → store and surface recommendation
                if isinstance(result, dict) and result.get("blocked"):
                    pending_blocked = result
                    response = result["message"]
                    tool_name = result["tool_call"].get("name", "unknown tool")
                    print(f"\nAI: {response}")
                    print(f"\n⚠️  Action requires approval: [{tool_name}]")
                    print("   Type 'yes' to confirm or anything else to cancel.\n")
                    print("-" * 50 + "\n")
                    # Save this recommendation turn to history so the LLM
                    # has context when Turn 2 arrives.
                    chat_history.append(HumanMessage(content=user_input))
                    chat_history.append(AIMessage(content=response))
                    continue  # Wait for Turn 2 without saving another history entry

                response = result if isinstance(result, str) else extract_response_text(result)
                print(f"AI: {response}\n")
                print("-" * 50 + "\n")

                # Persist this turn into history so the agent remembers
                # its Phase 1 recommendation when the user says "yes".
                chat_history.append(HumanMessage(content=user_input))
                chat_history.append(AIMessage(content=response))

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit.")
                continue
            except EOFError:
                print("\n\nGoodbye!")
                break
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()