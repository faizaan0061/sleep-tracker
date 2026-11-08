# Recovery Tracker — how to start it (every time)

Whenever you sit down to work on this, do this:

1. In VS Code: **File → Open Folder → recovery-tracker**
   (open THIS folder, not your home folder — that's what fixes the `~` problem)
2. **Terminal → New Terminal**
3. Type:
   ```
   bash run.sh
   ```
4. Open your browser to **http://127.0.0.1:8000/docs**

To stop the server: click the terminal and press **Ctrl+C**.

That's it. `run.sh` moves into the folder, turns on the virtual
environment, and starts the server — all the steps you used to do by hand.

---

## If `bash run.sh` ever fails

**"No such file or directory: venv/bin/activate"**
→ The virtual environment is missing. Rebuild it once:
```
cd ~/Documents/Projects/recovery-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Then `bash run.sh` works again.

**"No module named uvicorn" (or fastapi, or sqlmodel)**
→ Packages aren't installed in this venv. Fix:
```
source venv/bin/activate
pip install -r requirements.txt
```

---

## The two things that caused every past snag

1. **Which folder am I in?** The terminal prompt should end in
   `recovery-tracker`. If it ends in `~`, you're in your home folder and
   nothing will be found. `run.sh` handles this for you now.

2. **Which environment is on?** The prompt should show `(venv)`. That's
   the project's isolated Python. `run.sh` turns it on for you now.

---

## What's built so far

- `GET  /`              → health check ("backend is running")
- `POST /api/checkin`   → save one morning check-in
- `GET  /api/checkins`  → read all check-ins, each with a readiness score

Data lives in `recovery.db` (a single SQLite file in this folder).
