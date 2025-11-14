import streamlit as st
from db import list_users, add_or_update_user, deactivate_user
import re, binascii, secrets, hashlib
from ensure_db import init_db, DATABASE_URL
from config import SETUP_SECRET_ENV

def hash_password(password: str, salt: bytes=None, iterations: int=200_000):
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return {
        "algorithm": "pbkdf2_sha256",
        "iterations": iterations,
        "salt": binascii.hexlify(salt).decode(),
        "hash": binascii.hexlify(dk).decode()
    }

def valid_password(p):
    if len(p) < 8: return False, "Minimum 8 characters required"
    if not re.search(r"[A-Z]", p): return False, "At least one uppercase letter required"
    if not re.search(r"[a-z]", p): return False, "At least one lowercase letter required"
    if not re.search(r"[0-9]", p): return False, "At least one digit required"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]", p): return False, "At least one special character required"
    return True, ""

class AdminDashboard:
    def __init__(self, app):
        self.app = app
        init_db(insert_default_admin=True)

    def run(self):
        st.title("Admin Dashboard")
        tabs = st.tabs(["Users","Permissions","System"])
        with tabs[0]:
            st.subheader("Users")
            users = list_users()
            for u in users:
                cols = st.columns([2,1,1])
                cols[0].write(u['username'])
                cols[1].write(u['role'])
                if cols[2].button(f"Deactivate##{u['username']}"):
                    deactivate_user(u['username'])
                    st.experimental_rerun()
            st.markdown('---')
            st.subheader("Create user")
            with st.form('create'):
                username = st.text_input("Username")
                password = st.text_input("Password", type='password')
                role = st.selectbox("Role", ["user","admin"])
                submitted = st.form_submit_button("Create / Update")
                if submitted:
                    ok, msg = valid_password(password)
                    if not ok:
                        st.error(msg)
                    else:
                        h = hash_password(password)
                        add_or_update_user(username, h['algorithm'], h['iterations'], h['salt'], h['hash'], role)
                        st.success("User created/updated")
        with tabs[1]:
            st.subheader("Permissions (simple)")
            st.write("Page permissions feature placeholder — extend as needed.")
            st.write("You can later implement fine-grained permissions here.")
        with tabs[2]:
            st.subheader("System")
            st.write(f"Database URL (detected): {DATABASE_URL}")
            st.write("Environment-based auto-init and default admin insertion is enabled.")
