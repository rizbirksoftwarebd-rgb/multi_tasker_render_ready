# Multi-Tasker — Render-Ready Streamlit App (Auto DB Init)

This project auto-detects Render's managed Postgres via environment variables and will:
- Create tables on first start
- Insert the default admin user (from `backup_auth.json`) if no admin exists
- Provide Admin Dashboard for user management and page permission placeholders
- Fall back to a JSON-based auth if DB connection entirely fails (last resort)

Default admin username: **admin**
Default admin password: **Admin@12345**

Deploy steps:
1. Push repo to GitHub.
2. Create a Web Service on Render and connect the repo.
3. Add a PostgreSQL Database in Render (managed) — Render will set the DB env var automatically.
4. Deploy; app will auto-create tables and seed default admin if needed.
