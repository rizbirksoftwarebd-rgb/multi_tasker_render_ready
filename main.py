import streamlit as st
from config import APP_TITLE, LOGO_PATH, SETUP_SECRET_ENV
from auth.auth import Auth
from home.home import HomePage
from about.about import AboutPage
from admin.admin_dashboard import AdminDashboard
import ensure_db, json, os
from db import get_user

def load_css(path):
    try:
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass

class App:
    def __init__(self):
        st.set_page_config(page_title=APP_TITLE, page_icon=LOGO_PATH, layout='wide')
        # Try to init DB using ensure_db; if fails, app will continue but DB operations may fail
        try:
            # insert_default_admin True ensures default admin from backup_auth.json is added if no admin exists
            ensure_db.init_db(insert_default_admin=True, backup_json_path='backup_auth.json')
            self.db_mode = 'sql'
        except Exception as e:
            # fallback to JSON mode
            self.db_mode = 'json'
            st.warning('Database connection failed — running in JSON fallback mode.')
        self.auth = Auth()
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = None

    def show_login(self):
        load_css('home/home.css')
        st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:78vh'>", unsafe_allow_html=True)
        st.markdown("<div class='card' style='max-width:520px;padding:28px'>", unsafe_allow_html=True)
        st.image(LOGO_PATH, width=200)
        st.header('Sign in')
        uname = st.text_input('Username')
        pwd = st.text_input('Password', type='password')
        if st.button('Sign in'):
            ok, msg = self.auth.authenticate(uname.strip(), pwd)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = uname.strip()
                st.rerun()
            else:
                st.error(msg or 'Invalid credentials')
        st.markdown('</div></div>', unsafe_allow_html=True)

    def show_app(self):
        load_css('home/home.css')
        with st.sidebar:
            st.image(LOGO_PATH, width=140)
            st.markdown('### Navigation')
            role = self.auth.get_role(st.session_state.username)
            if role == 'admin':
                page = st.radio('Go to', ['Home','About','Admin'])
            else:
                page = st.radio('Go to', ['Home','About'])
            st.markdown('---')
            if st.button('Logout'):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()

        if page == 'Home':
            HomePage(self).run()
        elif page == 'About':
            AboutPage(self).run()
        else:
            if role != 'admin':
                st.error('Access denied')
            else:
                AdminDashboard(self).run()

def main():
    app = App()
    if not st.session_state.logged_in:
        app.show_login()
    else:
        app.show_app()

if __name__ == '__main__':
    main()
