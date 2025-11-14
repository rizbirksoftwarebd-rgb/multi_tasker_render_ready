import streamlit as st
class AboutPage:
    def __init__(self, app): self.app = app
    def run(self):
        st.title('About')
        st.write('Multi-Tasker — Render-ready deployment demo.')
