from app import DB
from datetime import datetime


class Chat(DB.Model):
    __tablename__ = 'chat'

    id = DB.Column(DB.Integer, primary_key=True)
    dt = DB.Column(DB.DateTime)
    user1_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    user1_name = DB.Column(DB.String(32), DB.ForeignKey('user.username'))
    user2_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    user2_name = DB.Column(DB.String(32), DB.ForeignKey('user.username'))
    last_message_dt = DB.Column(DB.DateTime)

    def __init__(self, user1_id, user1_name, user2_id, user2_name):
        self.dt = datetime.utcnow()
        self.user1_id = user1_id
        self.user1_name = user1_name
        self.user2_id = user2_id
        self.user2_name = user2_name
        self.last_message_dt = datetime.utcnow()


    def __repr__(self):
        return '<Chat %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'dt': self.dt.isoformat(),
            'user1_id': self.user1_id,
            'user1_name': self.user1_name,
            'user2_id': self.user2_id,
            'user2_name': self.user2_name,
            'last_message_dt': self.last_message_dt.isoformat()
        }

def get_chat(id):
    # Search by primary key
    return Chat.query.get(id)

def check_if_chat_exists(id):
    return (get_chat(id) is not None)

def create_chat(user1_id, user1_name, user2_id, user2_name):
    # Create Chat instance
    new_chat = Chat(user1_id, user1_name, user2_id, user2_name)
    # Insert into table
    DB.session.add(new_chat)
    # Commit
    DB.session.commit()
    return new_chat.id

def get_chats_for_user(user_id):
    # Get all chats where given user is a participant
    return Chat.query.filter((Chat.user1_id == user_id) | (Chat.user2_id == user_id)).all()

def update_chat_last_message_time(chat_id, last_message_dt):
    # Find chat with given id
    chat = get_chat(chat_id)
    # Update last message time
    chat.last_message_dt = last_message_dt
    # Commit
    DB.session.commit()
