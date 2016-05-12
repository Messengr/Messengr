import os
import sqlite3
import bcrypt

from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for

import settings
import db

app = Flask(__name__)
app.config.from_object(settings)

DB = db.setup(app.config['DATABASE'])


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
            return render_template('index.html', chats=DB.get_chat(user_id), username=session['user']['username'], error="This user does not exist.")
        receiver = DB.find_user_by_name(receiver_username)
        chat_id = DB.create_chat(user_id, username, receiver['id'], receiver['username'])
        return redirect(url_for('chat', id=chat_id))

    return render_template('index.html', chats=DB.get_chat(user_id), username=session['user']['username'])


@app.route('/about')
def about():
    return render_template('about.html')


# @app.route('/admin', methods=['GET', 'POST'])
# def admin():
#     if not 'logged_in' in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         # This little hack is needed for testing due to how Python dictionary keys work
#         DB.delete_message([k[6:] for k in request.form.keys()])
#         redirect(url_for('admin'))

#     messages = DB.get_message()
#     messages.reverse()

#     return render_template('admin.html', messages=messages)


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
    if len(request.form['username']) == 0 or " " in request.form['username']:
        return jsonify({'error': "Invalid username. Must be nonempty and contain no spaces."})
    if len(request.form['password']) < 8:
        return jsonify({'error': "Invalid password. Must be at least 8 characters."})
    if DB.check_if_user_exists(request.form['username']):
        return jsonify({'error': "Username already taken."})

    username = request.form['username']
    password = request.form['password']
    pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # TODO: Replace with actual public key
    err = DB.add_user_to_db(username, pass_hash, "public_key")
    if err == None:
        return jsonify({'error': "Unexpected error."})
    session['logged_in'] = True
    session['user'] = DB.find_user_by_name(username)
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/chat/<int:id>', methods=['GET'])
def chat(id):
    user_id = session['user']['id']
    chat = DB.get_chat(user_id, id)
    if not chat or (user_id != chat[0]['user1_id'] and user_id != chat[0]['user2_id']):
        return make_response(jsonify({'error': 'Not found'}), 404)
    messages = DB.get_chat_messages(id)
    other_user = chat[0]['user1_name']
    if user_id == chat[0]['user1_id']:
        other_user = chat[0]['user2_name']
    return render_template('chat.html', messages=messages, user=user_id, other_user=other_user)


# # RESTful routing (serves JSON to provide an external API)
# @app.route('/messages/api', methods=['GET'])
# @app.route('/messages/api/<int:id>', methods=['GET'])
# def get_message_by_id(id=None):
#     messages = DB.get_message(id)
#     if not messages:
#         return make_response(jsonify({'error': 'Not found'}), 404)

#     return jsonify({'messages': messages})


# @app.route('/messages/api', methods=['POST'])
# def create_message():
#     if not request.json or not 'message' in request.json or not 'receiver' in request.json or not session['logged_in']:
#         return make_response(jsonify({'error': 'Bad request'}), 400)
    
#     receiver = request.json['receiver']
#     user = session['user']
#     id = DB.add_message(request.json['message'], user, receiver)

#     return get_message_by_id(id), 201


# @app.route('/messages/api/<int:id>', methods=['DELETE'])
# def delete_message_by_id(id):
#     DB.delete_message(id)
#     return jsonify({'result': True})


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
    app.run(host='0.0.0.0', debug=True)
