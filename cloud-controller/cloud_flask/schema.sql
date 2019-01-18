PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS thing;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  amazon_id TEXT NOT NULL,
  pubnub_publish_key TEXT DEFAULT NULL,
  pubnub_subscribe_key TEXT DEFAULT NULL
);

CREATE TABLE thing (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  endpoint_id TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  UNIQUE(endpoint_id, user_id) ON CONFLICT REPLACE
  CONSTRAINT fk_thing_user FOREIGN KEY (user_id) REFERENCES user(id)
);