import os
import sqlite3
import bcrypt
from string import ascii_lowercase

from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, join_room, leave_room, send, emit

import settings
import db

app = Flask(__name__)
app.config.from_object(settings)
socketio = SocketIO(app)

DB = db.setup(app.config['DATABASE'])

VALID_USERNAME_CHARS = set(['-', '_'] + [str(i) for i in xrange(0,10)] + list(ascii_lowercase))

# Standard routing (server-side rendered pages)
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'logged_in' in session and 'user' in session:
        user_id = session['user']['id']
        username = session['user']['username']
    else:
        return redirect(url_for('login'))

    if request.method == 'POST':
        receiver_username = request.form['receiver']
        if not DB.check_if_user_exists(receiver_username):
            return render_template('index.html', chats=DB.get_chats_for_user(user_id), username=session['user']['username'], error="This user does not exist.")
        receiver = DB.find_user_by_name(receiver_username)
        chat_id = DB.create_chat(user_id, username, receiver['id'], receiver['username'])
        return redirect(url_for('chat', id=chat_id))

    return render_template('index.html', chats=DB.get_chats_for_user(user_id), username=session['user']['username'])


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] and request.form['password'] and DB.user_authenticated(request.form['username'], request.form['password']):
            session['logged_in'] = True
            session['user'] = DB.find_user_by_name(request.form['username'])
            return redirect(url_for('home'))
        else:
            error = 'Invalid username and/or password'
    return render_template('login.html', error=error)


@app.route('/user/create', methods=['POST'])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password') 
    public_key = request.form.get('public_key')

    
    error = None
    if None in [username, password, public_key]:
        error  = "Request missing a field!"
    if len(username) == 0 or len(username) > 16:
        error = "Invalid username. Must be nonempty and contain at most 16 characters."
    if len([c for c in username if c.lower() not in VALID_USERNAME_CHARS]) > 0:
        error = "Invalid username. Must contain only letters (a-z), numbers (0-9), dashes (-), underscores (_)."
    if len(password) < 8:
        error = "Invalid password. Must be at least 8 characters."
    if DB.check_if_user_exists(username):
        error = "Username already taken."
    
    if error is not None:
        return render_template('login.html', error=error)    
    pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    no_err = DB.add_user_to_db(username, pass_hash, public_key)
    if no_err is None:
        return jsonify({'error': "Unexpected error."})
    session['logged_in'] = True
    session['user'] = DB.find_user_by_name(username)
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('chat_id', None)
    return redirect(url_for('login'))


@app.route('/chat/<int:id>')
def chat(id):
    # Check that user is logged in
    if 'logged_in' not in session or 'user' not in session:
        return redirect(url_for('login'))
    user_id = session['user']['id']
    username = session['user']['username']
    # Check that this chat exists and user is valid participant
    chat = DB.get_chat(id)
    if not chat or (user_id != chat['user1_id'] and user_id != chat['user2_id']):
        return make_response(jsonify({'error': 'Not found'}), 404)
    chat_id = chat['id']
    session['chat_id'] = chat_id
    # Get the 'other' user in the chat
    other_userid = chat['user1_id']
    other_username = chat['user1_name']
    if user_id == chat['user1_id']:
        other_userid = chat['user2_id']
        other_username = chat['user2_name']
    messages = DB.get_chat_messages(id)
    return render_template('chat.html', chat_id=chat_id, messages=messages, user=user_id, other_user=other_username)


@socketio.on('joined', namespace='/chat')
def joined(data):
    """Sent by clients when they enter a chat.
    A status message is broadcast to all people in the chat."""
    if 'logged_in' not in session or 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']['username']
    chat_id = session['chat_id']
    if username is None or chat_id is None:
        return make_response(jsonify({'error': 'Not found'}), 404)
    chat = DB.get_chat(chat_id)
    if username != chat['user1_name'] and username != chat['user2_name']:
        return make_response(jsonify({'error': 'Not found'}), 404)
    join_room(chat_id)
    emit('username', {'username': username}, room=request.sid)
    emit('status', {'msg': username + ' has entered the room.'}, room=chat_id)


@socketio.on('new_message', namespace='/chat')
def new_message(data):
    """Sent by a client when the user entered a new message.
    The message is sent to both people in the chat."""
    if 'logged_in' not in session or 'user' not in session:
        return redirect(url_for('login'))
    message = data['msg']
    user_id = session['user']['id']
    username = session['user']['username']
    chat_id = session['chat_id']
    if None in [message, user_id, chat_id]:
        return make_response(jsonify({'error': 'Not found'}), 404)
    chat = DB.get_chat(chat_id)
    if username != chat['user1_name'] and username != chat['user2_name']:
        return make_response(jsonify({'error': 'Not found'}), 404)
    # Get the 'other' user in the chat
    other_userid = chat['user1_id']
    other_username = chat['user1_name']
    if user_id == chat['user1_id']:
        other_userid = chat['user2_id']
        other_username = chat['user2_name']
    # Insert into DB
    msg_id = DB.add_message(message, user_id, username, other_userid, other_username, chat_id)
    msg = DB.get_message(msg_id)
    if len(msg) != 1:
        return make_response(jsonify({'error': 'Not found'}), 404)
    msg = msg[0]
    emit('message', {
        'sender': msg['sender_username'],
        'receiver': msg['receiver_username'],
        'msg': msg['message'],
        'dt': msg['dt']
    }, room=chat_id)


@socketio.on('left', namespace='/chat')
def left(data):
    """Sent by clients when they leave a chat.
    A status message is broadcast to both people in the chat."""
    if 'logged_in' not in session or 'user' not in session:
        return redirect(url_for('login'))
    chat_id = session['chat_id']
    if chat_id is None:
        return make_response(jsonify({'error': 'Not found'}), 404)
    chat = DB.get_chat(chat_id)
    username = session['user']['username']
    if chat is None or username is None:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if username != chat['user1_name'] and username != chat['user2_name']:
        return make_response(jsonify({'error': 'Not found'}), 404)
    leave_room(session['chat_id'])
    session['chat_id'] = None


if __name__ == '__main__':

    # Test whether the database exists; if not, create it and create the table
    if not os.path.exists(app.config['DATABASE']):
        try:
            conn = sqlite3.connect(app.config['DATABASE'])

            # Absolute path needed for testing environment
            sql_path = os.path.join(app.config['APP_ROOT'], 'db_init.sql')
            cmd = open(sql_path, 'r').read()
            c = conn.cursor()
            c.executescript(cmd)
            conn.commit()
            conn.close()
        except IOError:
            print "Couldn't initialize the database, exiting..."
            raise
        except sqlite3.OperationalError:
            print "Couldn't execute the SQL, exiting..."
            raise
    socketio.run(app)
