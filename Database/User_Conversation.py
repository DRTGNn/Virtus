from Database.db import User, Conversation, Message, SessionLocal

def create_user(username):
    db = SessionLocal()

    user = User(username=username)
    db.add(user)

    db.commit()
    db.refresh(user)

    return user

def create_conversation(user_id):
    db = SessionLocal()

    conv = Conversation(user_id=user_id)

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return conv

def save_message(conversation_id, role, content):

    db = SessionLocal()

    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(msg)
    db.commit()

