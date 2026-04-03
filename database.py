"""SQLite access for the Finance Management System."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parent / "fms.db"
PBKDF2_ITERATIONS = 100_000


@contextmanager
def get_conn() -> Any:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                risk_level TEXT
            )
            """
        )


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"{salt}${dk.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, hex_hash = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return dk.hex() == hex_hash


def create_user(username: str, password: str) -> int:
    pw_hash = _hash_password(password)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, risk_level) VALUES (?, ?, NULL)",
            (username.strip(), pw_hash),
        )
        return int(cur.lastrowid)


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, username, password_hash, risk_level FROM users WHERE username = ?",
            (username.strip(),),
        )
        return cur.fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, username, password_hash, risk_level FROM users WHERE id = ?",
            (user_id,),
        )
        return cur.fetchone()


def verify_login(username: str, password: str) -> Optional[int]:
    row = get_user_by_username(username)
    if row is None:
        return None
    if not _verify_password(password, row["password_hash"]):
        return None
    return int(row["id"])


def update_user_risk_level(user_id: int, risk_level: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET risk_level = ? WHERE id = ?",
            (risk_level, user_id),
        )
