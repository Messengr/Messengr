from app import DB
from datetime import datetime
import bcrypt

class User(DB.Model):
    __tablename__ = 'user'

    id = DB.Column(DB.Integer, primary_key=True)
    dt = DB.Column(DB.DateTime)
    username = DB.Column(DB.String(32), unique=True)
    pass_hash = DB.Column(DB.String(128))
    public_key = DB.Column(DB.String(256))

    def __init__(self, username, pass_hash, public_key):
        self.dt = datetime.utcnow()
        self.username = username
        self.pass_hash = pass_hash
        self.public_key = public_key

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        return {
            'id': self.id,
            'dt': self.dt.isoformat(),
            'username': self.username,
            'pass_hash': self.pass_hash,
            'public_key': self.public_key
        }


def find_user_by_name(username):
    # Query using username and return first
    # If user not found, None is returned
    return User.query.filter_by(username=username).first()

def check_if_user_exists(username):
    user_exists = (find_user_by_name(username) is not None)
    return user_exists

def add_user_to_db(username, password, public_key):
    # Generate salt
    salt = bcrypt.gensalt()
    # Hash given password using salt
    pass_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Create User instance
    new_user = User(username, pass_hash, public_key)
    # Insert to table
    DB.session.add(new_user)
    # Commit
    DB.session.commit()
    # Return the new user's id
    return new_user.id

def user_authenticated(username, password):
    # Query for this username
    user = find_user_by_name(username)
    if user is None:
        # User not found
        return False
    # Get user hashed password
    hashed = user.pass_hash.encode('utf-8')
    # Hash given password using salt and compare to stored hash
    return (bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed)
