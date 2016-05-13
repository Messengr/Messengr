CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY,
  dt TEXT NOT NULL,
  message TEXT NOT NULL,
  sender_id INTEGER NOT NULL,
  sender_username TEXT NOT NULL,
  receiver_id INTEGER NOT NULL,
  receiver_username TEXT NOT NULL,
  chat_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  dt TEXT NOT NULL,
  username TEXT NOT NULL,
  pass_hash TEXT NOT NULL,
  public_key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chats (
  id INTEGER PRIMARY KEY,
  dt TEXT NOT NULL,
  user1_id INTEGER NOT NULL,
  user1_name TEXT NOT NULL,
  user2_id INTEGER NOT NULL,
  user2_name TEXT NOT NULL,
  last_message_dt TEXT NOT NULL
);

