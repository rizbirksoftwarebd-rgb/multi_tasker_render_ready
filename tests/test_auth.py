from ensure_db import init_db
from db import add_or_update_user
import binascii, secrets, hashlib
from auth.auth import Auth

def hash_password(password: str, salt: bytes=None, iterations: int=200000):
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return {'algorithm':'pbkdf2_sha256','iterations':iterations,'salt':binascii.hexlify(salt).decode(),'hash':binascii.hexlify(dk).decode()}

def setup_module():
    init_db()
    h = hash_password("Test@1234")
    add_or_update_user("testuser", h['algorithm'], h['iterations'], h['salt'], h['hash'], role='user')

def test_auth_success():
    a = Auth()
    ok, msg = a.authenticate("testuser", "Test@1234")
    assert ok is True

def test_auth_fail():
    a = Auth()
    ok, msg = a.authenticate("testuser", "wrongpass")
    assert ok is False
