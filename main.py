"""
Sleep Tracker — backend
Full stack: database, auth (register/login), and check-in endpoints.

Run with:
    python -m uvicorn main:app --reload
Then open http://127.0.0.1:8000
"""

import secrets
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import bcrypt as _bcrypt
from sqlmodel import Field, SQLModel, Session, create_engine, select


# ---------------------------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------------------------
# Passwords must NEVER be stored as plain text.
# We store a bcrypt hash instead — a one-way scramble.
# hash_password and check_password are the only two places we touch passwords.
def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------------------------

class User(SQLModel, table=True):
    """One row = one registered account."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    # unique=True means no two users can share a username.
    # index=True tells the database to build a lookup table for fast searches.
    password_hash: str


class UserSession(SQLModel, table=True):
    """
    One row = one login session (a token the browser holds).
    When a user logs in, we create a random token and store it here.
    The browser sends that token with every request to prove who they are.
    This is called "token-based authentication."
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # foreign_key means this column points to a row in the User table.
    token: str = Field(unique=True, index=True)


class DailyLog(SQLModel, table=True):
    """One row = one day's check-in."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    # user_id links each check-in to the user who submitted it,
    # so users only ever see their own data.
    date: date
    resting_hr: int
    sleep_hours: float
    soreness: int
    energy: int
    mood: int
    cardio_minutes: int = Field(default=0)

    # ── HABITS ──────────────────────────────────────────────────────────
    # Each habit is a simple True/False (did they do it or not).
    # To add a new habit: copy one of these lines and change the name.
    # Then add the same field to CheckInCreate below, and add a button
    # in the Habits card in index.html. That's all you need.
    alcohol_use: bool = Field(default=False)
    naps:        bool = Field(default=False)
    # ── ADD MORE HABITS HERE ─────────────────────────────────────────────
    # Example: meditation: bool = Field(default=False)
    # Example: caffeine:   bool = Field(default=False)
    # Example: screen_time_limited: bool = Field(default=False)


# ---------------------------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------------------------
engine = create_engine("sqlite:///recovery.db")
SQLModel.metadata.create_all(engine)
# create_all is safe to run every startup — it only creates tables that
# don't already exist, and leaves existing ones alone.


# ---------------------------------------------------------------------------
# INPUT MODELS (separate from table models so Pydantic handles coercion)
# ---------------------------------------------------------------------------

class UserCreate(SQLModel):
    username: str
    password: str  # plain text coming in — we hash it before saving


class CheckInCreate(SQLModel):
    date: date
    resting_hr: int
    sleep_hours: float
    soreness: int
    energy: int
    mood: int
    cardio_minutes: int = 0
    # ── HABITS (mirror the fields in DailyLog above) ─────────────────
    alcohol_use: bool = False
    naps:        bool = False
    # ── ADD MORE HABITS HERE ─────────────────────────────────────────
    # Example: meditation: bool = False


# ---------------------------------------------------------------------------
# AUTH HELPER
# ---------------------------------------------------------------------------

def get_current_user(authorization: str = Header(...)) -> User:
    """
    This is a "dependency" — FastAPI calls it automatically on any route
    that includes it. It reads the Authorization header the browser sends,
    looks up the token in the database, and returns the matching User.

    If the token is missing or invalid, it raises a 401 error and the
    route never runs. This is how we protect endpoints.

    The browser sends:  Authorization: Bearer <token>
    We strip "Bearer " and check the token against UserSession.
    """
    # Strip the "Bearer " prefix to get the raw token string
    token = authorization.replace("Bearer ", "").strip()

    with Session(engine) as session:
        user_session = session.exec(
            select(UserSession).where(UserSession.token == token)
        ).first()

        if not user_session:
            raise HTTPException(status_code=401, detail="Invalid or expired token. Please log in again.")

        user = session.get(User, user_session.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found.")

        return user


# ---------------------------------------------------------------------------
# APP + ROUTES
# ---------------------------------------------------------------------------
app = FastAPI(title="Sleep Tracker API")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/checkin")
def read_checkin():
    return FileResponse("static/checkin.html")


# ── REGISTER ────────────────────────────────────────────────────────────────
@app.post("/api/register")
def register(data: UserCreate):
    """
    Create a new account.
    1. Check the username isn't already taken.
    2. Hash the password.
    3. Save the new user to the database.
    """
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.username == data.username)
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Username already taken.")

        if len(data.password.encode()) > 72:
            raise HTTPException(status_code=400, detail="Password must be 72 characters or fewer.")

        user = User(username=data.username, password_hash=hash_password(data.password))
        session.add(user)
        session.commit()

        return {"message": "Account created. You can now log in."}


# ── LOGIN ────────────────────────────────────────────────────────────────────
@app.post("/api/login")
def login(data: UserCreate):
    """
    Log in to an existing account.
    1. Find the user by username.
    2. Verify the password against the stored hash.
    3. Generate a random token, save it, and return it to the browser.
    """
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == data.username)
        ).first()

        # Note: we check both "user not found" and "wrong password" with the
        # same error message. This prevents attackers from learning which
        # usernames exist.
        if not user or not check_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password.")

        # secrets.token_hex(32) generates a cryptographically random 64-character
        # string. This is your session token — impossible to guess.
        token = secrets.token_hex(32)
        user_session = UserSession(user_id=user.id, token=token)
        session.add(user_session)
        session.commit()

        return {"token": token, "username": user.username}


# ── LOGOUT ───────────────────────────────────────────────────────────────────
@app.post("/api/logout")
def logout(authorization: str = Header(...)):
    """Delete the session token so it can never be used again."""
    token = authorization.replace("Bearer ", "").strip()

    with Session(engine) as session:
        user_session = session.exec(
            select(UserSession).where(UserSession.token == token)
        ).first()

        if user_session:
            session.delete(user_session)
            session.commit()

    return {"message": "Logged out."}


# ── SAVE A CHECK-IN (protected) ──────────────────────────────────────────────
@app.post("/api/checkin")
def create_checkin(data: CheckInCreate, authorization: str = Header(...)):
    """Save a check-in tied to the logged-in user."""
    user = get_current_user(authorization)
    log  = DailyLog(**data.dict(), user_id=user.id)
    with Session(engine) as session:
        session.add(log)
        session.commit()
        session.refresh(log)
        return log


# ── USER COUNT ───────────────────────────────────────────────────────────────
@app.get("/api/stats")
def get_stats():
    """Returns total number of registered users."""
    with Session(engine) as session:
        count = len(session.exec(select(User)).all())
        return {"total_users": count}


# ── GET CHECK-INS (protected — only returns the logged-in user's data) ────────
@app.get("/api/checkins")
def get_checkins(authorization: str = Header(...)):
    """Return the current user's check-ins with a computed readiness score."""
    user = get_current_user(authorization)
    with Session(engine) as session:
        logs = session.exec(
            select(DailyLog).where(DailyLog.user_id == user.id)
        ).all()

        results = []
        for log in logs:
            score = round(
                (log.sleep_hours / 9 * 100) * 0.30 +
                ((6 - log.soreness) / 5 * 100) * 0.25 +
                (log.energy / 5 * 100) * 0.20 +
                (log.mood / 5 * 100) * 0.15 +
                (min(log.cardio_minutes, 90) / 90 * 100) * 0.10
            )
            results.append({**log.dict(), "readiness_score": score})

        return results
