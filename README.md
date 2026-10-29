# Modular AI Website Builder

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Install Chromium: `python -m playwright install chromium`
4. Copy `backend/.env.example` to `backend/.env` and set `GOOGLE_API_KEY`.

## Run backend

From the project root:

`python -m uvicorn backend.app:app --reload --port 8000`

API docs: http://127.0.0.1:8000/docs

## Run frontend

Open a second terminal at the project root:

`python -m streamlit run frontend/app.py`

## Notes

- The backend owns LangGraph, Gemini, Playwright, and SQLite checkpointing.
- The Streamlit frontend communicates with the backend over HTTP.
- Browser tests are heuristic and do not prove every interaction works.
- This is a local development starter. Add authentication and stricter isolation before exposing the API to a network.
