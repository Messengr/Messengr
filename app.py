import os
from string import ascii_lowercase
import functools

import config
from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room, send, emit, disconnect
from flask_sslify import SSLify


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
socketio = SocketIO(app)
sslify = SSLify(app)

# Import models
DB = SQLAlchemy(app)
import models

# Usernames must contain only letters (a-z), numbers (0-9), dashes (-), underscores (_)
VALID_USERNAME_CHARS = set(['-', '_'] + [str(i) for i in xrange(0,10)] + list(ascii_lowercase))

# Standard routing (server-side rendered pages)
@app.route('/')
def home():
    # Check if user is logged in
    if 'logged_in' in session and 'user' in session:
        user_id = session['user']['id']
        username = session['user']['username']
    else:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))

    # Deliver home page
    chats = [chat.to_dict() for chat in models.get_chats_for_user(user_id)]
    return render_template('index.html', chats=chats, username=username)

@app.route('/public_key')
def get_public_key():
    # Check if user is logged in
    if 'logged_in' in session and 'user' in session:
        sender_public_key = session['user']['public_key']
    else:
        # User is not logged in, return error message
        return jsonify({'error': "Unauthorized request."})
    # Get receiver_username from request
    receiver_username = request.args.get('receiver_username', '')
    # Make sure that the receiver exists
    if not models.check_if_user_exists(receiver_username):
        return jsonify({"error": "This user does not exist."})
    # Find receiver user
    receiver = models.find_user_by_name(receiver_username)
    return jsonify(sender_public_key=sender_public_key, receiver_public_key=receiver.public_key)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'logged_in' in session and 'user' in session:
        # If so, redirect to home page
        return redirect(url_for('home'))
    error = None
    # Attempt to login a user
    if request.method == 'POST':
        # Check that entered username/password pair is valid
        if request.form['username'] and request.form['password'] and models.user_authenticated(request.form['username'], request.form['password']):
            session['logged_in'] = True
            session['user'] = models.find_user_by_name(request.form['username']).to_dict()
            return redirect(url_for('home'))
        else:
            error = 'Invalid username and/or password'
    # Deliver login page
    return render_template('login.html', error=error)


@app.route('/user/create', methods=['POST'])
def create_user():
    # Check if user is already logged in
    if 'logged_in' in session and 'user' in session:
        # If so, redirect to home page
        return redirect(url_for('home'))
    username = request.form.get('username')
    password = request.form.get('password') 
    public_key = request.form.get('public_key')

    # Validate entered username and password
    error = None
    if None in [username, password, public_key]:
        error  = "Request missing a field!"
    if len(username) == 0 or len(username) > 16:
        error = "Invalid username. Must be nonempty and contain at most 16 characters."
    if len([c for c in username if c.lower() not in VALID_USERNAME_CHARS]) > 0:
        error = "Invalid username. Must contain only letters (a-z), numbers (0-9), dashes (-), underscores (_)."
    if len(password) < 8:
        error = "Invalid password. Must be at least 8 characters."
    if models.check_if_user_exists(username):
        error = "Username already taken."
    
    # Invalid username or password
    if error is not None:
        return render_template('login.html', error=error)

    # Add new user to database
    id = models.add_user_to_db(username, password, public_key)
    if id is None:
        # Database error
        return jsonify({'error': "Unexpected error."})

    # Redirect new user to home page
    session['logged_in'] = True
    session['user'] = models.find_user_by_name(username).to_dict()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    # Clear stored session variables
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('chat_id', None)
    return redirect(url_for('login'))

@app.route('/chat/create', methods=['POST'])
def create_chat():
    # Check if user is logged in
    if 'logged_in' in session and 'user' in session:
        user_id = session['user']['id']
        username = session['user']['username']
        sender_public_key = session['user']['public_key']
    else:
        # User is not logged in, return error message
        return jsonify({'error': "Unauthorized request."})
    sk_sym_1 = request.form.get('sk_sym_1', '')
    sk_sym_2 = request.form.get('sk_sym_2', '')
    receiver_username = request.form.get('receiver_username', '')
    receiver_public_key = request.form.get('receiver_public_key', '')
    if '' in [sk_sym_1, sk_sym_2, receiver_username, receiver_public_key]:
        return jsonify({'error': "Unable to create chat."})
    receiver = models.find_user_by_name(receiver_username)
    if (receiver is None) or (receiver.public_key != receiver_public_key):
        return jsonify({'error': "Unexpected error."})
    chat_id = models.create_chat(user_id, username, sk_sym_1, receiver.id, receiver.username, sk_sym_2)
    return jsonify(chat_id=chat_id)

@app.route('/chat/<int:id>')
def chat(id):
    # Check that user is logged in
    if 'logged_in' not in session or 'user' not in session:
        return redirect(url_for('login'))
    user_id = session['user']['id']
    username = session['user']['username']
    # Check that this chat exists and user is valid participant
    chat = models.get_chat(id)
    if not chat or (user_id != chat.user1_id and user_id != chat.user2_id):
        return make_response(jsonify({'error': 'Not found'}), 404)
    chat_id = chat.id
    session['chat_id'] = chat_id
    # Get the 'other' user in the chat
    other_userid = chat.user1_id
    other_username = chat.user1_name
    if user_id == chat.user1_id:
        other_userid = chat.user2_id
        other_username = chat.user2_name
    # Get messages for this chat and render the chat view
    messages = [message.to_dict() for message in models.get_chat_messages(id)]
    return render_template('chat.html', chat_id=chat_id, messages=messages, user=user_id, other_user=other_username)

# Ensure authentication before handling socketio messages
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # Disconnect socket if user not logged in
        if 'logged_in' not in session or 'user' not in session:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketio.on('joined', namespace='/chat')
@authenticated_only
def joined(data):
    """Sent by clients when they enter a chat.
    A status message is broadcast to all people in the chat."""
    username = session['user']['username']
    chat_id = session['chat_id']
    # Safety check
    if username is None or chat_id is None:
        return False
    chat = models.get_chat(chat_id)
    # Check that user is valid participant in chat
    if username != chat.user1_name and username != chat.user2_name:
        return False
    # Join chat room
    join_room(chat_id)
    # Send current user to client
    emit('username', {'username': username}, room=request.sid)
    emit('status', {'msg': username + ' has entered the room.'}, room=chat_id)


@socketio.on('new_message', namespace='/chat')
@authenticated_only
def new_message(data):
    """Sent by a client when the user entered a new message.
    The message is sent to both people in the chat."""
    message = data['msg']
    user_id = session['user']['id']
    username = session['user']['username']
    chat_id = session['chat_id']
    # Safety check
    if None in [message, user_id, chat_id] or len(message) == 0 or len(message) > 128:
        return False
    chat = models.get_chat(chat_id)
    # Check that user is valid participant in chat
    if username != chat.user1_name and username != chat.user2_name:
        return False
    # Get the 'other' user in the chat
    other_userid = chat.user1_id
    other_username = chat.user1_name
    if user_id == chat.user1_id:
        other_userid = chat.user2_id
        other_username = chat.user2_name
    # Insert message into DB
    msg = models.add_message(message, user_id, username, other_userid, other_username, chat_id)
    # TODO: Check that this does not give error?
    # Update the chat's last message time
    models.update_chat_last_message_time(chat_id, msg.dt)
    # Send message back to client
    emit('message', {
        'sender': msg.sender_username,
        'receiver': msg.receiver_username,
        'msg': msg.text,
        'dt': msg.dt.isoformat()
    }, room=chat_id)


@socketio.on('left', namespace='/chat')
@authenticated_only
def left(data):
    """Sent by clients when they leave a chat.
    A status message is broadcast to both people in the chat."""
    chat_id = session['chat_id']
    # Safety check
    if chat_id is None:
        return False
    # Fetch chat from database
    chat = models.get_chat(chat_id)
    username = session['user']['username']
    # Safety check
    if chat is None or username is None:
        return False
    # Check that user is valid participant in chat
    if username != chat.user1_name and username != chat.user2_name:
        return False
    # Leave room and reset session variable for chat id
    leave_room(session['chat_id'])
    session['chat_id'] = None


if __name__ == '__main__':

    # Run app
    socketio.run(app)
