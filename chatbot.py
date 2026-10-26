"""
chatbot.py
Step 7 - The main file. Run this file to start the chatbot.
"""

from google.genai import errors

import analytics
import chat_logger
from gemini_client import GeminiChatbot

HELP_TEXT = """
Commands:
  /history - show your last 5 chats (Pandas)
  /stats   - show chat statistics (NumPy)
  /charts  - save charts as images (Matplotlib + Seaborn)
  /models  - list Gemini models your key can use
  /reset   - forget the conversation and start fresh
  /help    - show this help
  /exit    - close the chatbot
Anything else you type is sent to Gemini as a question.
"""


def show_history():
    """Show the last 5 chats from the CSV file."""
    df = chat_logger.load_history()
    if df.empty:
        print("No chats saved yet.")
        return
    last_five = df[["chat_no", "question", "response_time_sec"]].tail(5)
    print(last_five.to_string(index=False))


def main():
    print("=" * 50)
    print("  AI CHATBOT  (powered by Google Gemini)")
    print("  Type /help to see commands.")
    print("=" * 50)

    try:
        bot = GeminiChatbot()
    except ValueError as error:
        print(f"Setup problem: {error}")
        return

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # ----- Commands -----
        if user_input == "/exit":
            print("Goodbye!")
            break
        elif user_input == "/help":
            print(HELP_TEXT)
        elif user_input == "/history":
            show_history()
        elif user_input == "/stats":
            analytics.show_summary(chat_logger.load_history())
        elif user_input == "/charts":
            analytics.create_charts(chat_logger.load_history())
        elif user_input == "/models":
            try:
                print("\n".join(bot.list_models()))
            except Exception as error:
                print(f"Could not list models: {error}")
        elif user_input == "/reset":
            bot.reset()
            print("Conversation reset.")

        # ----- A normal question: send it to Gemini -----
        else:
            try:
                print("Gemini is thinking...")
                answer, seconds = bot.ask(user_input)
            except errors.APIError as error:
                print(f"Gemini API error ({error.code}): {error.message}")
                continue
            except Exception as error:
                print(f"Something went wrong: {error}")
                continue

            print(f"\nGemini: {answer}")
            print(f"\n(answered in {seconds} sec)")
            chat_logger.save_chat(user_input, answer, seconds)


if __name__ == "__main__":
    main()
