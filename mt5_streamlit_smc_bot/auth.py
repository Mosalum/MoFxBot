from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

import streamlit as st


PASSWORD_HASH = "b1f5cdbff554e37a87655e5c6225cc23fc533adba990e9f3908fbecd90208837"
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_SECONDS = 120
SESSION_TIMEOUT_SECONDS = 20 * 60


@dataclass
class AuthStatus:
    authenticated: bool
    failed_attempts: int
    lock_until: float
    last_activity: float


def initialize_auth_state() -> None:
    defaults = {
        "authenticated": False,
        "failed_attempts": 0,
        "lock_until": 0.0,
        "last_activity": 0.0,
        "session_expired": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str) -> bool:
    if not password:
        return False
    return hash_password(password) == PASSWORD_HASH


def get_auth_status() -> AuthStatus:
    return AuthStatus(
        authenticated=bool(st.session_state.get("authenticated", False)),
        failed_attempts=int(st.session_state.get("failed_attempts", 0)),
        lock_until=float(st.session_state.get("lock_until", 0.0)),
        last_activity=float(st.session_state.get("last_activity", 0.0)),
    )


def is_locked() -> tuple[bool, int]:
    now = time.time()
    lock_until = float(st.session_state.get("lock_until", 0.0))
    if lock_until > now:
        return True, int(lock_until - now)
    if lock_until:
        st.session_state["lock_until"] = 0.0
        st.session_state["failed_attempts"] = 0
    return False, 0


def register_failed_attempt() -> None:
    attempts = int(st.session_state.get("failed_attempts", 0)) + 1
    st.session_state["failed_attempts"] = attempts
    if attempts >= MAX_FAILED_ATTEMPTS:
        st.session_state["lock_until"] = time.time() + LOCK_DURATION_SECONDS


def login(password: str) -> bool:
    locked, _ = is_locked()
    if locked:
        return False

    if verify_password(password):
        st.session_state["authenticated"] = True
        st.session_state["failed_attempts"] = 0
        st.session_state["lock_until"] = 0.0
        touch_activity()
        return True

    register_failed_attempt()
    return False


def logout(session_expired: bool = False) -> None:
    st.session_state["authenticated"] = False
    st.session_state["last_activity"] = 0.0
    st.session_state["session_expired"] = session_expired


def touch_activity() -> None:
    st.session_state["last_activity"] = time.time()


def enforce_session_timeout() -> bool:
    if not st.session_state.get("authenticated", False):
        return False

    last_activity = float(st.session_state.get("last_activity", 0.0))
    if not last_activity:
        touch_activity()
        return False

    if time.time() - last_activity > SESSION_TIMEOUT_SECONDS:
        logout(session_expired=True)
        return True

    return False
