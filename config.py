"""
config.py
Step 3 - All settings of our chatbot live in this one file.
"""

import os
from dotenv import load_dotenv

# Read the hidden .env file and load its values into the environment
load_dotenv()

# 1. Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

# 2. Chatbot personality (this is called a "system prompt")
SYSTEM_PROMPT = (
    "You are a friendly AI assistant for students. "
    "Answer clearly in simple English. "
    "Use short sentences and small examples when helpful."
)

# 3. Where we save our files
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "chat_history.csv")
CHARTS_DIR = "charts"
