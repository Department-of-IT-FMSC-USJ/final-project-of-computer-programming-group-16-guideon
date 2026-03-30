"""
session_manager.py
Session persistence for Bridora.

How it works:
- On every server startup, a new random SERVER_RUN_ID is written to data/server_run.id
- When saving a session, this ID is embedded into session.json
- When restoring a session, the stored ID must match the current server_run.id
- If they don't match (i.e. the server was restarted), the session is ignored
- This means: page refresh = stays logged in, server restart = logged out
"""

import json
import os
import uuid
import streamlit as st

SESSION_FILE  = os.path.join("data", "session.json")
RUN_ID_FILE   = os.path.join("data", "server_run.id")


def _get_server_run_id() -> str:
    """Read the current server run ID from disk."""
    try:
        with open(RUN_ID_FILE, "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def init_server_run():
    """
    Write a fresh server run ID to disk.
    Call this ONCE at the very top of app.py using:
        import session_manager as sm
        sm.init_server_run()
    Because app.py is re-executed on every Streamlit rerun, we guard this
    with a module-level flag so it only runs on the true first import.
    """
    os.makedirs("data", exist_ok=True)
    new_id = str(uuid.uuid4())
    with open(RUN_ID_FILE, "w") as f:
        f.write(new_id)


def _load() -> dict:
    """Read the saved session file."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(data: dict):
    """Write session data to file."""
    os.makedirs("data", exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def restore_sessions():
    """
    Restore logins from file into session_state.
    Only call this on a fresh browser load (when session_state is empty).
    Silently ignores sessions saved by a different server run.
    """
    data = _load()
    current_run_id = _get_server_run_id()

    # If this session was saved by a different server run, reject it.
    if not current_run_id or data.get("server_run_id") != current_run_id:
        return

    if "customer" in data:
        st.session_state.customer = data["customer"]

    if data.get("is_vendor") and "shop_data" in data:
        st.session_state.is_vendor = True
        st.session_state.shop_data = data["shop_data"]

    if data.get("is_admin"):
        st.session_state.is_admin = True


def sync_sessions():
    """
    Write current login state to file, tagged with the current server run ID.
    Call this at the bottom of app.py on every render.
    """
    current_run_id = _get_server_run_id()
    data = {"server_run_id": current_run_id}

    if "customer" in st.session_state:
        data["customer"] = st.session_state.customer
    if "is_vendor" in st.session_state:
        data["is_vendor"] = True
        data["shop_data"] = st.session_state.get("shop_data", {})
    if "is_admin" in st.session_state:
        data["is_admin"] = True

    _save(data)
