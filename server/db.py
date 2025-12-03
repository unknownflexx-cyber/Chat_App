from models import SessionLocal, User, Message
from auth import hash_password, verify_password


# Here we create a session to the database
def get_db():
    return SessionLocal()


# Here we are creating new users
def create_user(username, plain_password):
    db = get_db()

    # check if some with the same username exists already
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        db.close()
        return False, "Username already exists"

    # Hashing the password to make the password more secure
    hashed = hash_password(plain_password)

    # Here we are creating a new user
    new_user = User(username=username, password_hash=hashed)

    db.add(new_user)
    db.commit()
    db.close()

    return True, "User created successfully"


# Here we are verifying if the user exists and if the password is correct
def verify_user(username, plain_password):
    db = get_db()

    user = db.query(User).filter_by(username=username).first()
    if not user:
        db.close()
        return False

    result = verify_password(plain_password, user.password_hash)
    db.close()

    return result


# Here we are using this function to store the messages in the database
def save_message(sender_username, content):
    db = get_db()

    msg = Message(sender=sender_username, receiver="ALL", text=content)
    db.add(msg)
    db.commit()
    # Ensure autoincremented ID is loaded before closing session
    db.refresh(msg)
    mid = msg.id
    db.close()
    return mid


# Here we are getting the messages after a certain id
def get_messages_after(last_id: int):
    db = get_db()

    msgs = (
        db.query(Message)
        .filter(Message.id > last_id)
        .order_by(Message.id.asc())
        .all()
    )
    db.close()

    return msgs

