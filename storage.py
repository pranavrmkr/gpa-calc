import json
import secrets
import sqlite3
import time
from pathlib import Path

from flask.sessions import SessionInterface, SessionMixin


class SavedSession(dict, SessionMixin):
    def __init__(self, data=None, sid=None):
        super().__init__(data or {})
        self.sid = sid or secrets.token_hex(32)


class SQLiteSessions(SessionInterface):
    def connect(self, app):
        path = Path(app.config["DATABASE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, data TEXT NOT NULL, expires REAL NOT NULL)")
        return connection

    def open_session(self, app, request):
        sid = request.cookies.get(self.get_cookie_name(app), "")
        if len(sid) != 64 or any(c not in "0123456789abcdef" for c in sid):
            return SavedSession()
        with self.connect(app) as db:
            row = db.execute("SELECT data FROM sessions WHERE id = ? AND expires > ?",
                             (sid, time.time())).fetchone()
        return SavedSession(json.loads(row[0]), sid) if row else SavedSession()

    def save_session(self, app, session, response):
        response.vary.add("Cookie")
        lifetime = int(app.permanent_session_lifetime.total_seconds())
        with self.connect(app) as db:
            db.execute("DELETE FROM sessions WHERE expires <= ?", (time.time(),))
            if not session:
                db.execute("DELETE FROM sessions WHERE id = ?", (session.sid,))
            else:
                db.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?, ?)",
                           (session.sid, json.dumps(dict(session), allow_nan=False), time.time() + lifetime))
        if not session:
            response.delete_cookie(self.get_cookie_name(app), path=self.get_cookie_path(app),
                                   domain=self.get_cookie_domain(app))
        else:
            response.set_cookie(self.get_cookie_name(app), session.sid, max_age=lifetime,
                                httponly=True, secure=self.get_cookie_secure(app),
                                samesite="Lax", path=self.get_cookie_path(app),
                                domain=self.get_cookie_domain(app))
