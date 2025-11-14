from ensure_db import get_engine, users, permissions
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

engine = get_engine()

def add_or_update_user(username, algorithm, iterations, salt, hashhex, role="user", active=1):
    stmt = insert(users).values(username=username, algorithm=algorithm, iterations=iterations, salt=salt, hash=hashhex, role=role, active=active)
    # ON CONFLICT... behavior: use text for cross-backend compatibility
    upsert = stmt.on_conflict_do_update(index_elements=[users.c.username],
                                        set_=dict(algorithm=algorithm, iterations=iterations, salt=salt, hash=hashhex, role=role, active=active))
    with engine.connect() as conn:
        conn.execute(upsert)
        conn.commit()

def get_user(username):
    stmt = select(users).where(users.c.username == username)
    with engine.connect() as conn:
        r = conn.execute(stmt).mappings().fetchone()
        return dict(r) if r else None

def list_users():
    stmt = select(users.c.username, users.c.role, users.c.active)
    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().fetchall()
        return [dict(r) for r in rows]

def deactivate_user(username):
    stmt = update(users).where(users.c.username==username).values(active=0)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
