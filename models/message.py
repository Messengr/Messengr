from app import DB
from datetime import datetime

class Message(DB.Model):
    __tablename__ = 'messages'

    id = DB.Column(DB.Integer, primary_key=True)
    dt = DB.Column(DB.DateTime)
    text = DB.Column(DB.String(128))
    sender_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    sender_username = DB.Column(DB.String(32))
    receiver_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    receiver_username = DB.Column(DB.String(32))
    chat_id = DB.Column(DB.Integer, DB.ForeignKey('chat.id'))

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

def add_message(text, sender_id, sender_username, receiver_id, receiver_username, chat_id):
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
