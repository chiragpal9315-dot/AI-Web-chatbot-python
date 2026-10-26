"""
analytics.py
Step 6 - Study our chats with NumPy, Matplotlib and Seaborn.
"""

import os

import matplotlib
matplotlib.use("Agg")   # save charts as image files (no pop-up window)
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import config

sns.set_theme(style="whitegrid")


def show_summary(df):
    """Print simple statistics using NumPy."""
    if df.empty:
        print("No chats yet. Ask a question first!")
        return

    times = df["response_time_sec"].to_numpy()
    q_words = df["question_words"].to_numpy()
    a_words = df["answer_words"].to_numpy()

    print("\n----- CHAT SUMMARY -----")
    print(f"Total chats           : {len(df)}")
    print(f"Average response time : {np.mean(times):.2f} sec")
    print(f"Median response time  : {np.median(times):.2f} sec")
    print(f"Slowest response      : {np.max(times):.2f} sec")
    print(f"Average answer length : {np.mean(a_words):.0f} words")

    # Simple prediction: draw a straight line through the data
    if len(df) >= 3 and np.std(q_words) > 0:
        slope, intercept = np.polyfit(q_words, a_words, 1)
        guess = max(slope * 10 + intercept, 0)
        print(f"Predicted answer for a 10-word question: {guess:.0f} words")
    print("------------------------\n")


def _save_chart(filename):
    """Save the current chart as a PNG image and close it."""
    os.makedirs(config.CHARTS_DIR, exist_ok=True)
    path = os.path.join(config.CHARTS_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Saved: {path}")


def create_charts(df):
    """Make 3 charts from the chat history."""
    if len(df) < 2:
        print("Ask at least 2 questions before creating charts.")
        return

    # Chart 1 (Seaborn): how fast is Gemini?
    plt.figure(figsize=(7, 4))
    sns.histplot(df["response_time_sec"], bins=10, color="steelblue")
    plt.title("Gemini Response Time")
    plt.xlabel("Seconds")
    plt.ylabel("Number of chats")
    _save_chart("1_response_time.png")

    # Chart 2 (Seaborn): do longer questions get longer answers?
    plt.figure(figsize=(7, 4))
    can_fit_line = df["question_words"].nunique() > 1
    sns.regplot(x="question_words", y="answer_words", data=df,
                color="darkgreen", fit_reg=can_fit_line)
    plt.title("Question Length vs Answer Length")
    plt.xlabel("Words in question")
    plt.ylabel("Words in answer")
    _save_chart("2_question_vs_answer.png")

    # Chart 3 (Matplotlib): response time of every chat
    plt.figure(figsize=(7, 4))
    plt.plot(df["chat_no"], df["response_time_sec"],
             marker="o", color="darkorange")
    plt.title("Response Time of Each Chat")
    plt.xlabel("Chat number")
    plt.ylabel("Seconds")
    _save_chart("3_time_per_chat.png")
