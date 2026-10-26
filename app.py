"""Flask web server for the Gemini chatbot.

The chatbot logic (gemini_client, chat_logger, analytics) is reused as-is;
this file only exposes it over HTTP as a small JSON API.
"""
import os
import threading

import numpy as np
from flask import Flask, jsonify, render_template, request, send_from_directory
from google.genai import errors

import analytics
import chat_logger
import config
from gemini_client import GeminiChatbot

app = Flask(__name__)

# One shared bot instance (single-user, local app). The lock keeps
# concurrent requests from interleaving messages in the same conversation.
bot = None
bot_lock = threading.Lock()
setup_error = None

try:
    bot = GeminiChatbot()
except ValueError as exc:  # e.g. missing API key
    setup_error = str(exc)


# ---------- Pages ----------
@app.route("/")
def index():
    return render_template("index.html", model=config.MODEL_NAME)


# ---------- Chat ----------
@app.route("/api/chat", methods=["POST"])
def chat():
    if bot is None:
        return jsonify(error=f"Setup problem: {setup_error}"), 500

    question = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not question:
        return jsonify(error="Please type a message."), 400

    try:
        with bot_lock:
            answer, seconds = bot.ask(question)
    except errors.APIError as exc:
        return jsonify(error=f"Gemini API error ({exc.code}): {exc.message}"), 502
    except Exception as exc:
        return jsonify(error=f"Something went wrong: {exc}"), 500

    chat_logger.save_chat(question, answer, seconds)
    return jsonify(answer=answer, seconds=seconds)


@app.route("/api/reset", methods=["POST"])
def reset():
    if bot is None:
        return jsonify(error=f"Setup problem: {setup_error}"), 500
    with bot_lock:
        bot.reset()
    return jsonify(ok=True)


# ---------- History ----------
@app.route("/api/history")
def history():
    """Return the saved chats (oldest first) so the page can restore them."""
    df = chat_logger.load_history()
    rows = df[["chat_no", "question", "answer", "response_time_sec"]]
    return jsonify(rows.to_dict(orient="records"))


# ---------- Stats (NumPy) ----------
@app.route("/api/stats")
def stats():
    df = chat_logger.load_history()
    if df.empty:
        return jsonify(empty=True)

    times = df["response_time_sec"].to_numpy()
    q_words = df["question_words"].to_numpy()
    a_words = df["answer_words"].to_numpy()

    result = {
        "empty": False,
        "total": int(len(df)),
        "avg_time": round(float(np.mean(times)), 2),
        "median_time": round(float(np.median(times)), 2),
        "max_time": round(float(np.max(times)), 2),
        "avg_words": round(float(np.mean(a_words))),
        "prediction": None,
    }
    # Same rule as analytics.show_summary: simple linear fit on 3+ chats
    if len(df) >= 3 and np.std(q_words) > 0:
        slope, intercept = np.polyfit(q_words, a_words, 1)
        result["prediction"] = round(max(float(slope * 10 + intercept), 0))
    return jsonify(result)


# ---------- Charts (Matplotlib + Seaborn) ----------
CHART_FILES = [
    ("1_response_time.png", "Response time distribution"),
    ("2_question_vs_answer.png", "Question vs answer length"),
    ("3_time_per_chat.png", "Response time per chat"),
]


@app.route("/api/charts", methods=["POST"])
def charts():
    df = chat_logger.load_history()
    if len(df) < 2:
        return jsonify(error="Ask at least 2 questions before creating charts."), 400
    analytics.create_charts(df)
    return jsonify(charts=[
        {"title": title, "url": f"/charts/{name}"} for name, title in CHART_FILES
    ])


@app.route("/charts/<path:filename>")
def serve_chart(filename):
    response = send_from_directory(os.path.abspath(config.CHARTS_DIR), filename)
    response.headers["Cache-Control"] = "no-store"  # always show fresh charts
    return response


# ---------- Models ----------
@app.route("/api/models")
def models():
    if bot is None:
        return jsonify(error=f"Setup problem: {setup_error}"), 500
    try:
        return jsonify(models=bot.list_models())
    except Exception as exc:
        return jsonify(error=f"Could not list models: {exc}"), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)
