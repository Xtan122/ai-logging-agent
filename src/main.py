#!/usr/bin/env python3
"""
AI Logging Agent
Main entry point for the interactive agent
"""
import sys
from langchain_core.messages import HumanMessage, AIMessage
from .agents import LogAnalyzerAgent
from .config import Config

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
                    print("Chat history cleared.")
                    continue
                elif user_input.lower() == 'help':
                    print_banner()
                    continue

                print("Processing your query...")
                response = agent.process_query(user_input, chat_history)
                print(f"AI: {response}\n")
                print("-" * 50 + "\n")  # Separator for readability

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