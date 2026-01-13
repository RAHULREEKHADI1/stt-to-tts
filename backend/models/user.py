from config.db import get_db
import bcrypt

def create_user(email, password):
    db = get_db()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.users.insert_one({
        "email": email,
        "password": hashed
    })

def find_user(email):
    db = get_db()
    return db.users.find_one({"email": email})
