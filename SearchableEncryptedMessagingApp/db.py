import sqlite3
import bcrypt

def setup(db_config):
    return DatabaseHelper(db_config)

class DatabaseHelper(object):
    def __init__(self, db_config):
        self.db_config = db_config

    # Helper functions
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

            return [{'id': r[0], 'dt': r[1], 'message': r[2], 'sender': r[3]} for r in rows]


    def add_message(self, message, sender, receiver):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "INSERT INTO messages VALUES (NULL, datetime('now'),?,?)"
            c.execute(q, (message, sender))
            conn.commit()
            return c.lastrowid


    def delete_message(self, ids):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "DELETE FROM messages WHERE id=?"

            # Try/catch in case 'ids' isn't an iterable
            try:
                for i in ids:
                    c.execute(q, (int(i),))
            except TypeError:
                c.execute(q, (int(ids),))

            conn.commit()

    def check_if_user_exists(self, username):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "SELECT * FROM users WHERE username=?"
            rows = c.execute(q, (username,)).fetchall()
            user_exists =  (len(rows) == 1)
            return user_exists

    def add_user_to_db(self, username, pass_hash):
        with sqlite3.connect(self.db_config) as conn:
            c = conn.cursor()
            q = "INSERT INTO users VALUES (NULL, datetime('now'),?,?)"
            c.execute(q, (username, pass_hash))
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
            # Get user hashed password
            hashed = rows[0][3]
            # Hash given password using salt
            return (bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed)
