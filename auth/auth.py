import hashlib, binascii
from db import get_user

def verify_password(stored, provided) -> bool:
    if not stored:
        return False
    algo = stored.get("algorithm")
    if algo != "pbkdf2_sha256":
        return False
    iterations = int(stored.get("iterations", 100000))
    salt = binascii.unhexlify(stored["salt"])
    stored_hash = stored["hash"]
    dk = hashlib.pbkdf2_hmac("sha256", provided.encode(), salt, iterations)
    return binascii.hexlify(dk).decode() == stored_hash

class Auth:
    def __init__(self):
        pass

    def authenticate(self, username, password):
        user = get_user(username)
        if not user:
            return False, "Invalid credentials."
        if int(user.get("active",1)) == 0:
            return False, "Account is deactivated."
        ok = verify_password(user, password)
        if ok:
            return True, None
        return False, "Invalid credentials."

    def get_role(self, username):
        user = get_user(username)
        return user.get("role") if user else None
