import os, json, binascii, time
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, text
from sqlalchemy.exc import OperationalError

# Detect Render's DB environment variables first
DB_ENV_VARS = ["DATABASE_URL","RENDER_DATABASE_URL","RENDER_EXTERNAL_POSTGRES_URL"]

def get_db_url():
    for v in DB_ENV_VARS:
        vval = os.environ.get(v)
        if vval:
            return vval
    # fallback to sqlite file
    return "sqlite:///app.db"

DATABASE_URL = get_db_url()

engine = create_engine(DATABASE_URL, future=True)

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("username", String, primary_key=True),
    Column("algorithm", String, nullable=False),
    Column("iterations", Integer, nullable=False),
    Column("salt", String, nullable=False),
    Column("hash", String, nullable=False),
    Column("role", String, nullable=False, server_default="user"),
    Column("active", Integer, nullable=False, server_default="1")
)

permissions = Table(
    "permissions", metadata,
    Column("page", String, primary_key=True),
    Column("role", String, nullable=False)
)

def init_db(insert_default_admin=False, backup_json_path="backup_auth.json"):
    try:
        metadata.create_all(engine)
    except OperationalError as e:
        # fallback attempt: if driver can't connect, raise to let caller handle fallback
        raise

    if insert_default_admin:
        # check if any admin exists
        with engine.connect() as conn:
            res = conn.execute(text("SELECT username FROM users WHERE role='admin' LIMIT 1")).fetchone()
            if not res:
                # load backup json and insert admin
                try:
                    data = json.loads(open(backup_json_path).read())
                    admin = data.get("admin")
                    if admin:
                        ins = users.insert().values(
                            username="admin",
                            algorithm=admin["algorithm"],
                            iterations=int(admin.get("iterations",100000)),
                            salt=admin["salt"],
                            hash=admin["hash"],
                            role="admin",
                            active=1
                        )
                        conn.execute(ins)
                        conn.commit()
                except Exception as e:
                    # cannot insert admin; ignore silently
                    pass

def get_engine():
    return engine
