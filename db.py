from ensure_db import get_engine, users, permissions
from sqlalchemy import select, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

engine = get_engine()

def add_or_update_user(username, algorithm, iterations, salt, hashhex, role="user", active=1):
    """
    Upsert user safely.
    - For PostgreSQL: use on_conflict_do_update
    - For SQLite or other backends: use merge() fallback
    """
    try:
        # Detect backend
        backend = engine.url.get_backend_name()
        if backend == "postgresql":
            stmt = pg_insert(users).values(
                username=username,
                algorithm=algorithm,
                iterations=iterations,
                salt=salt,
                hash=hashhex,
                role=role,
                active=active
            ).on_conflict_do_update(
                index_elements=[users.c.username],
                set_={
                    "algorithm": algorithm,
                    "iterations": iterations,
                    "salt": salt,
                    "hash": hashhex,
                    "role": role,
                    "active": active
                }
            )
        else:
            # Fallback for SQLite: merge
            stmt = users.merge().values(
                username=username,
                algorithm=algorithm,
                iterations=iterations,
                salt=salt,
                hash=hashhex,
                role=role,
                active=active
            )

        with engine.begin() as conn:
            conn.execute(stmt)
    except SQLAlchemyError as e:
        print("DB Error:", e)
        raise e

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
    stmt = update(users).where(users.c.username == username).values(active=0)
    with engine.begin() as conn:
        conn.execute(stmt)
