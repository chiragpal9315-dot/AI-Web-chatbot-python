# Gemini Chatbot – Web App

A Flask + HTML/CSS/JS front end for your existing Gemini chatbot.
The chatbot logic (`gemini_client.py`, `chat_logger.py`, `analytics.py`) is reused as-is.

## Project structure

```
.
├── app.py                # Flask server + JSON API
├── gemini_client.py      # (existing) Gemini chat wrapper
├── chat_logger.py        # (existing) pandas CSV logging
├── analytics.py          # (existing) NumPy stats + Matplotlib/Seaborn charts
├── config.py             # (existing) settings
├── chatbot.py            # (existing) original terminal version, still works
├── requirements.txt      # + flask
├── .env                  # your secrets (never commit this)
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file (see `.env.example`):
   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-flash-latest
   ```
   Get a free key at https://aistudio.google.com/apikey
3. Run:
   ```bash
   python app.py
   ```
4. Open http://127.0.0.1:5000

## Features

- Live chat with typing indicator, Enter to send, Shift+Enter for a new line
- Previous chats restored from `data/chat_history.csv` on reload
- Sidebar tools: statistics (NumPy), charts (Matplotlib + Seaborn), model list, reset, dark/light theme
- Responsive layout (sidebar collapses on mobile)

## API

| Route | Method | Purpose |
|---|---|---|
| `/api/chat` | POST `{message}` | Ask Gemini |
| `/api/reset` | POST | Start a fresh conversation |
| `/api/history` | GET | Saved chats |
| `/api/stats` | GET | Summary statistics |
| `/api/charts` | POST | Generate chart images |
| `/api/models` | GET | Models your key can use |

## Notes

- This is a single-user local app: all browser tabs share one conversation.
- `flask` is the only addition to your requirements.
