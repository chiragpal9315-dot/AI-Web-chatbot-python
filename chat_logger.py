"""
chat_logger.py
Step 5 - Save every question and answer using Pandas.
"""

import os
from datetime import datetime

import pandas as pd

import config

COLUMNS = [
    "chat_no", "timestamp", "question", "answer",
    "question_words", "answer_words", "response_time_sec",
]


def load_history():
    """Read the CSV file and return a DataFrame (empty if no file yet)."""
    if not os.path.exists(config.LOG_FILE):
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(config.LOG_FILE)


def save_chat(question, answer, response_time):
    """Add one new row to the CSV file."""
    os.makedirs(config.DATA_DIR, exist_ok=True)

    chat_no = len(load_history()) + 1
    new_row = pd.DataFrame([{
        "chat_no": chat_no,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer,
        "question_words": len(question.split()),
        "answer_words": len(answer.split()),
        "response_time_sec": response_time,
    }])

    file_is_new = not os.path.exists(config.LOG_FILE)
    new_row.to_csv(config.LOG_FILE, mode="a", header=file_is_new, index=False)
