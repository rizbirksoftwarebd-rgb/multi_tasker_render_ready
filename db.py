from ensure_db import get_engine, users, permissions
from sqlalchemy import select, insert, update, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as pg_insert

engine = get_engine()

def add_or_update_user(username, algorithm, iterations, salt, hashhex, role="user", active=1):
    backend = engine.url.get_backend_name()

    try:
        if backend == "postgresql":

            # Native PostgreSQL UPSERT
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

            with engine.begin() as conn:
                conn.execute(stmt)

        elif backend == "sqlite":

            # SQLite also supports ON CONFLICT DO UPDATE (raw SQL)
            stmt = text("""
                INSERT INTO users (username, algorithm, iterations, salt, hash, role, active)
                VALUES (:username, :algorithm, :iterations, :salt, :hash, :role, :active)
                ON CONFLICT(username) DO UPDATE SET
                    algorithm = excluded.algorithm,
                    iterations = excluded.iterations,
                    salt = excluded.salt,
                    hash = excluded.hash,
                    role = excluded.role,
                    active = excluded.active
            """)

            with engine.begin() as conn:
                conn.execute(stmt, {
                    "username": username,
                    "algorithm": algorithm,
                    "iterations": iterations,
                    "salt": salt,
                    "hash": hashhex,
                    "role": role,
                    "active": active
                })

        else:
            # Generic backend: manual fallback
            with engine.begin() as conn:
                existing = conn.execute(
                    select(users).where(users.c.username == username)
                ).fetchone()

                if existing is None:
                    conn.execute(
                        insert(users).values(
                            username=username,
                            algorithm=algorithm,
                            iterations=iterations,
                            salt=salt,
                            hash=hashhex,
                            role=role,
                            active=active
                        )
                    )
                else:
                    conn.execute(
                        update(users)
                        .where(users.c.username == username)
                        .values(
                            algorithm=algorithm,
                            iterations=iterations,
                            salt=salt,
                            hash=hashhex,
                            role=role,
                            active=active
                        )
                    )

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
