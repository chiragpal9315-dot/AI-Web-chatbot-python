"""
gemini_client.py
Step 4 - This file talks to Google Gemini.
"""

import time

from google import genai
from google.genai import types

import config

EMPTY_MESSAGE = "(Gemini returned an empty answer. Please rephrase.)"


class GeminiChatbot:
    """A small class that remembers the conversation with Gemini."""

    def __init__(self):
        # Stop early with a clear message if the key is missing
        if not config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. Create a .env file and add your key."
            )

        # Create the connection (called a client) to Gemini
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.chat = self._new_chat()

    def _new_chat(self):
        """Start a fresh conversation with our system prompt."""
        return self.client.chats.create(
            model=config.MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=config.SYSTEM_PROMPT
            ),
        )

    def ask(self, question):
        """Send a question to Gemini. Return (answer_text, seconds_taken)."""
        start = time.time()
        response = self.chat.send_message(question)
        seconds = round(time.time() - start, 2)

        answer = response.text or EMPTY_MESSAGE
        return answer, seconds

    def reset(self):
        """Forget the old conversation and start again."""
        self.chat = self._new_chat()

    def list_models(self):
        """Return names of models that can generate text."""
        names = []
        for model in self.client.models.list():
            actions = getattr(model, "supported_actions", None) or []
            if "generateContent" in actions:
                names.append(model.name)
        return names
