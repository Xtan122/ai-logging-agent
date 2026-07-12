#!/usr/bin/env python3
"""
AI Logging Agent
Main entry point for the interactive agent
"""
import sys
from .agents import LogAnalyzerAgent
from .config import Config

def print_banner():
    print("====================================")
    print("      AI Log Analyzer Agent         ")
    print("====================================")
    print("\nCapacities:")
    print("- Analyze log files for patterns and anomalies")
    print("- Provide insights and recommendations based on log data")
    print("- Interactive querying and reporting")
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

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue  # Skip empty input

                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting AI Log Analyzer. Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    agent.chat_history.clear()
                    print("Chat history cleared.")
                    continue
                elif user_input.lower() == 'help':
                    print_banner()
                    continue


                print("Processing your query...")
                response = agent.process_query(user_input)
                print(f"AI: {response}\n")
                print("-" * 50 + "\n")  # Separator for readability

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