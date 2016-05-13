import sqlite3
import bcrypt


CHAT_SCHEMA = (
    'id',
    'dt',
    'user1_id',
    'user1_name',
    'user2_id',
    'user2_name',
    'last_message_dt'
)

MESSAGE_SCHEMA = (
    'id',
    'dt',
    'message',
    'sender_id',
    'sender_username',
    'receiver_id',
    'receiver_username',
    'chat_id'
)

USER_SCHEMA = (
    'id',
    'dt',
    'username',
    'pass_hash',
    'public_key'
)


def setup(db_config):
    return DatabaseHelper(db_config)

class DatabaseHelper(object):
    def __init__(self, db_config):
        self.db_config = db_config


    ### Chat queries ###

    def check_if_chat_exists(self, id):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "SELECT * FROM chats WHERE id=?"
            rows = c.execute(q, (int(id),)).fetchall()
            chat_exists =  (len(rows) == 1)
            return chat_exists

    def create_chat(self, user1_id, user1_name, user2_id, user2_name):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "INSERT INTO chats VALUES (NULL, datetime('now'),?,?,?,?,datetime('now'))"
            c.execute(q, (user1_id, user1_name, user2_id, user2_name))
            conn.commit()
            return c.lastrowid

    def get_chats_for_user(self, user_id):
        """Return a list of chat objects (as dicts)"""
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "SELECT * FROM chats WHERE user1_id=? OR user2_id=? ORDER BY last_message_dt DESC"
            rows = c.execute(q, (user_id, user_id))
            return [ { CHAT_SCHEMA[i] : r[i] for i in xrange(len(CHAT_SCHEMA)) } for r in rows ]

    def get_chat(self, chat_id):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            chat_id = int(chat_id)
            q = "SELECT * FROM chats WHERE id=?"
            chat = c.execute(q, (chat_id,)).fetchone()
            if chat is None:
                return None
            return { CHAT_SCHEMA[i] : chat[i] for i in xrange(len(CHAT_SCHEMA)) }

    def get_chat_messages(self, chat_id):
        """Return a list of message objects (as dicts)"""
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            chat_id = int(chat_id)
            q = "SELECT * FROM messages WHERE chat_id=? ORDER BY dt ASC"
            rows = c.execute(q, (chat_id,))
            return [ { MESSAGE_SCHEMA[i] : r[i] for i in xrange(len(MESSAGE_SCHEMA)) } for r in rows ]

    def update_chat_last_message_time(self, chat_id, last_message_dt):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            chat_id = int(chat_id)
            q = "UPDATE chats SET last_message_dt=? WHERE id=?"
            c.execute(q, (last_message_dt, chat_id))
            conn.commit()

    ### Message queries ###

    def get_message(self, id=None):
        """Return a list of message objects (as dicts)"""
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()

            if id:
                id = int(id)  # Ensure that we have a valid id value to query
                q = "SELECT * FROM messages WHERE id=? ORDER BY dt DESC"
                rows = c.execute(q, (id,))

            else:
                q = "SELECT * FROM messages ORDER BY dt DESC"
                rows = c.execute(q)

            return [ { MESSAGE_SCHEMA[i] : r[i] for i in xrange(len(MESSAGE_SCHEMA)) } for r in rows ]

    def add_message(self, message, sender_id, sender_username, receiver_id, receiver_username, chat_id):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "INSERT INTO messages VALUES (NULL, datetime('now'),?,?,?,?,?,?)"
            c.execute(q, (message, sender_id, sender_username, receiver_id, receiver_username, chat_id))
            conn.commit()
            return c.lastrowid

    ### User queries ###

    def find_user_by_name(self, username):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "SELECT * FROM users WHERE username=?"
            rows = c.execute(q, (username,)).fetchall()
            if len(rows) > 0:
                user = rows[0]
                return {USER_SCHEMA[i] : user[i] for i in xrange(len(USER_SCHEMA))}
            return None

    def check_if_user_exists(self, username):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "SELECT * FROM users WHERE username=?"
            rows = c.execute(q, (username,)).fetchall()
            user_exists =  (len(rows) == 1)
            return user_exists

    def add_user_to_db(self, username, pass_hash, public_key):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            # First check if username already exists
            q = "SELECT * FROM users WHERE username=?"
            rows = c.execute(q, (username,)).fetchall()
            if len(rows) > 0:
                # Username already exists
                return None
            q = "INSERT INTO users VALUES (NULL, datetime('now'),?,?,?)"
            c.execute(q, (username, pass_hash, public_key))
            conn.commit()
            return c.lastrowid

    def user_authenticated(self, username, password):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "SELECT * FROM users WHERE username=?"
            rows = c.execute(q, (username,)).fetchall()
            if len(rows) != 1:
                # User not found
                return False
            # Get user
            user = rows[0]
            # Get right index of 'pass_hash'
            index = USER_SCHEMA.index('pass_hash')
            # Get user hashed password
            hashed = user[index].encode('utf-8')
            # Hash given password using salt
            return (bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed)

