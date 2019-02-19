import sqlite3
from typing import List, Tuple

import click
from flask import Flask
from flask import current_app as app
from flask import g
from flask.cli import with_appcontext


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db() -> None:
    db = get_db()

    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.execute('PRAGMA foreign_keys = ON')
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def create_or_update_user(email: str, amazon_id: str) -> int:
    db = get_db()
    user = find_user_by_email(email)
    if user is None:
        db.execute('INSERT INTO user (email, amazon_id) VALUES (?, ?)', (email, amazon_id))
    else:
        db.execute('UPDATE user SET email = ?, amazon_id = ? WHERE id = ?', (email, amazon_id, email))

    user_id = find_user_by_email(email)[0]
    db.commit()
    return user_id


def update_user_with_pubnub(user_id: int, pubnub_publish_key: str, pubnub_subscribe_key: str) -> int:
    db = get_db()
    user = find_user_by_id(user_id)
    if user is None:
        raise ValueError('User not found by id {}'.format(user_id))
    else:
        db.execute('UPDATE user SET pubnub_publish_key = ?, pubnub_subscribe_key = ? WHERE id = ?',
                   (pubnub_publish_key, pubnub_subscribe_key, user_id))

    db.commit()
    return user['id']


def get_user_pubnub_keys(user_id: int) -> Tuple[str, str]:
    db = get_db()
    res = db.execute('SELECT pubnub_publish_key, pubnub_subscribe_key FROM user WHERE id = ?', (user_id,)).fetchone()
    return (res['pubnub_publish_key'], res['pubnub_subscribe_key'])


def find_user_by_id(id: int) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()


def find_user_by_email(email: str) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()


def find_user_by_amazon_id(amazon_id: str) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM user WHERE amazon_id = ?', (amazon_id,)).fetchone()


def find_thing_by_endpoint_id_and_user_id(endpoint_id: str, user_id: int) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM thing WHERE endpoint_id = ? and user_id = ?', (endpoint_id, user_id)).fetchone()


def find_things_by_user_id(user_id: int) -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('SELECT * FROM thing WHERE user_id = ?', (user_id,)).fetchall()


def find_thing_by_id(id: int) -> sqlite3.Row:
    db = get_db()
    return db.execute('\
        SELECT t.id, endpoint_id, user_id, friendly_name, description, manufacturer_name, \
            ac.id as alexa_category_id, ac.name as alexa_category_name \
        FROM thing t \
        INNER JOIN alexa_category ac ON ac.id = t.alexa_category_id \
        WHERE t.id = ?', (id,)).fetchone()


def find_thing_capabilities_by_id(id: int) -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('\
        SELECT tacp.thing_id, tacp.alexa_capability_id as id, tacp.properties, ac.name as name \
        FROM thing_alexa_capability_properties tacp \
        INNER JOIN alexa_capability ac ON ac.id = tacp.alexa_capability_id \
        WHERE tacp.thing_id = ?', (id,)).fetchall()


def get_all_categories() -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('SELECT id, name FROM alexa_category').fetchall()


def get_all_capabilities() -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('SELECT id, name FROM alexa_capability').fetchall()
