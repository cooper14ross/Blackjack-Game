# Blackjack (Flask)

A minimal Blackjack game converted from your Processing sketch to Python (Flask) with a small HTML/CSS/JS UI.

## Run locally

```bash
# from this project folder
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
# then open http://127.0.0.1:5000
```

## Deploy to Render

1. Push this folder to a new GitHub repo.
2. On Render:
   - **New +** → **Web Service** → Connect your repo.
   - Runtime: **Python**.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add environment variable `SECRET_KEY` (optional) to override the Flask `app.secret_key`.
3. Deploy. Visit the generated URL.

## Notes

- Dealer starts with **one** card (matching your Processing code). Dealer draws to 17+ when you press **Stand**.
- If you want "standard" two-card dealer with one face-down card, you can adjust the initial deal and front-end reveal logic.
