"""
startup.py
Runs ONCE when the Streamlit server first imports it.
Writes a fresh server_run.id so that sessions from previous runs are invalidated.
"""
import session_manager as sm

# This will be executed the first time Python imports this module.
# Python caches imports, so this runs exactly once per server process lifetime.
sm.init_server_run()
