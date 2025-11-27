# db.py

from models import SessionLocal, User, Message
from auth import hash_password, verify_password


# -----------------------------
# Create DB Session
# -----------------------------
def get_db():
    return SessionLocal()


# -----------------------------
# USER FUNCTIONS
# -----------------------------
def create_user(username, plain_password):
    db = get_db()

    # Check existing user
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        db.close()
        return False, "Username already exists"

    # Hash the password
    hashed = hash_password(plain_password)

    # Create user
    new_user = User(username=username, password_hash=hashed)

    db.add(new_user)
    db.commit()
    db.close()

    return True, "User created successfully"


def get_user_by_username(username):
    db = get_db()

    user = db.query(User).filter_by(username=username).first()
    db.close()

    return user


def verify_user(username, plain_password):
    db = get_db()

    user = db.query(User).filter_by(username=username).first()
    if not user:
        db.close()
        return False

    result = verify_password(plain_password, user.password_hash)
    db.close()

    return result


# -----------------------------
# MESSAGE FUNCTIONS
# -----------------------------
def save_message(sender_username, content):
    db = get_db()

    msg = Message(sender=sender_username, receiver="ALL", text=content)
    db.add(msg)
    db.commit()
    db.close()
    return True


def get_messages_after(last_id: int):
    db = get_db()

    msgs = db.query(Message).filter(Message.id > last_id).order_by(Message.timestamp.asc()).all()
    db.close()

    return msgs
