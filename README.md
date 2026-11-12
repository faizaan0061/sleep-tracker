# Sleepker

An app used to track my sleep Log your morning vitals and see how your sleep, habits, and cardio affect how you feel — no wearable required.

**Live app:** https://sleep-tracker-cmw0.onrender.com

---
<h1>Leveraged Knowledge in<h1>

## Tech Stack

- **Python** — backend logic
- **FastAPI** — web framework / API
- **SQLModel** — database ORM
- **SQLite** — database
- **bcrypt** — password hashing
- **uvicorn** — web server
- **HTML / CSS / JavaScript** — frontend
- **Chart.js** — 10-day readiness chart

## DevOps

- **Git** — version control
- **GitHub / GitHub Desktop** — code hosting
- **Render** — cloud deployment
- **Virtual Environments (venv)** — Python dependency management

## Features

- User registration and login (token-based auth)
- Daily check-ins: sleep hours, resting heart rate, soreness, energy, mood, cardio
- Habits tracking: alcohol use, naps
- Readiness score (0–100) calculated from your inputs
- 10-day trend chart
- FAQ and info sections on the landing page

## Run Locally

1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the server: `python3 -m uvicorn main:app --reload`
6. Open `http://127.0.0.1:8000`
