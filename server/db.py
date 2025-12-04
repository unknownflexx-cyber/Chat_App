from typing import cast
from models import SessionLocal, User, Message
from auth import hash_password, verify_password


def get_db():
    """
    Here we are creating and returning a new SQLAlchemy database session.
    """
    return SessionLocal()
    

def create_user(username, plain_password):
    """
    Here we are creating a new user account if the username does not already exist.

  
    """
    db = get_db()

    existing = db.query(User).filter_by(username=username).first()
    if existing:
        db.close()
        return False, "Username already exists"

    hashed = hash_password(plain_password)

    new_user = User(username=username, password_hash=hashed)

    db.add(new_user)
    db.commit()
    db.close()

    return True, "User created successfully"


def verify_user(username, plain_password):
    """
    Here we are verifying user credentials during login.

    Args:
        username (str): The username attempting to log in.
        plain_password (str): The password entered by the user.

    Returns:
        bool: True if credentials are valid, otherwise False.
    """
    db = get_db()

    user = db.query(User).filter_by(username=username).first()
    if not user:
        db.close()
        return False

    result = verify_password(plain_password, cast(str, user.password_hash))
    db.close()

    return result


def save_message(sender_username, content):
    """
    Here we are saving a new chat message to the database.

    Args:
        sender_username (str): Username of the sender.
        content (str): The message text.

    Returns:
        tuple[int, str]: The auto-incremented ID and the ISO timestamp string.
    """
    db = get_db()

    msg = Message(sender=sender_username, receiver="ALL", text=content)
    db.add(msg)
    db.commit()
    # Ensure autoincremented ID is loaded before closing session
    db.refresh(msg)
    mid = msg.id
    ts = str(msg.timestamp)
    db.close()
    return mid, ts


def get_messages_after(last_id: int):
    """
    Here we are retrieving all messages with an ID greater than the given value.

    Args:
        last_id (int): The last message ID the client has received.

    Returns:
        list[Message]: Here we are returning all newer message objects sorted by ID.
    """
    db = get_db()

    msgs = (
        db.query(Message)
        .filter(Message.id > last_id)
        .order_by(Message.id.asc())
        .all()
    )
    db.close()

    return msgs

