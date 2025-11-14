#!/usr/bin/env python3
import getpass, re, binascii, secrets, hashlib, sys
from db import add_or_update_user
from ensure_db import init_db

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

def main():
    init_db(insert_default_admin=False)
    username = input('Enter username: ').strip()
    if not username:
        print('Username required.'); sys.exit(1)
    pwd = getpass.getpass('Enter password: ').strip()
    ok, msg = valid_password(pwd)
    if not ok:
        print("Password policy violation:", msg); sys.exit(1)
    pwd2 = getpass.getpass('Confirm password: ').strip()
    if pwd != pwd2:
        print('Passwords do not match.'); sys.exit(1)
    role = input('Role (admin/user) [user]: ').strip() or "user"
    h = hash_password(pwd)
    add_or_update_user(username, h['algorithm'], h['iterations'], h['salt'], h['hash'], role)
    print(f'User {username} added/updated in database.')

if __name__ == '__main__':
    main()
