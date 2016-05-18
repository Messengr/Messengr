from app import DB
from datetime import datetime
from sqlalchemy import asc

class Message(DB.Model):
    __tablename__ = 'messages'

    id = DB.Column(DB.Integer, primary_key=True)
    dt = DB.Column(DB.DateTime)
    text = DB.Column(DB.String(500))
    sender_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    sender_username = DB.Column(DB.String(32), DB.ForeignKey('users.username'))
    receiver_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    receiver_username = DB.Column(DB.String(32), DB.ForeignKey('users.username'))
    chat_id = DB.Column(DB.Integer, DB.ForeignKey('chats.id'))

    def __init__(self, text, sender_id, sender_username, receiver_id, receiver_username, chat_id):
        self.dt = datetime.utcnow()
        self.text = text
        self.sender_id = sender_id
        self.sender_username = sender_username
        self.receiver_id = receiver_id
        self.receiver_username = receiver_username
        self.chat_id = chat_id

    def __repr__(self):
        return '<Message %r>' % self.message

    def to_dict(self):
        return {
            'id': self.id,
            'dt': self.dt.isoformat(),
            'text': self.text,
            'sender_id': self.sender_id,
            'sender_username': self.sender_username,
            'receiver_id': self.receiver_id,
            'receiver_username': self.receiver_username,
            'chat_id': self.chat_id
        }


def get_message(id):
    # Search by primary key
    return Message.query.get(id)

def get_messages(message_ids):
    messages = Message.query.filter(Message.id.in_(message_ids)).order_by(Message.id.asc()).all()
    return messages

def add_message(text, sender_id, sender_username, receiver_id, receiver_username, chat_id):
    # Safety check
    if len(text) > 500 or len(sender_username) > 32 or len(receiver_username) > 32:
        return None
    # Create Message instance
    new_message = Message(text, sender_id, sender_username, receiver_id, receiver_username, chat_id)
    # Insert to table
    DB.session.add(new_message)
    # Commit
    DB.session.commit()
    # Return the new message
    return new_message

def get_chat_messages(chat_id):
    # Fetch all Messages in given chat
    return Message.query.filter_by(chat_id=chat_id).order_by(Message.dt).all()
