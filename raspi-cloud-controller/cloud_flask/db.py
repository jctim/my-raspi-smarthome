import sqlite3
from typing import List, Tuple

import click
from flask import Flask, g, current_app
from flask.cli import with_appcontext


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db() -> None:
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
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


########################################################################
# USER model functions                                                 #
########################################################################

def create_or_update_user(email: str, amazon_id: str) -> int:
    db = get_db()
    user = find_user_by_email(email)
    if user is None:
        db.execute('INSERT INTO user (email, amazon_id) VALUES (?, ?)', (email, amazon_id))
    else:
        db.execute('UPDATE user SET email = ?, amazon_id = ? WHERE id = ?', (email, amazon_id, user['id']))

    db.commit()
    user = find_user_by_email(email)
    return user['id']


def update_user_scope_uuid(user_id: int, user_scope_uuid: str) -> int:
    db = get_db()
    user = find_user_by_id(user_id)
    if user is None:
        raise ValueError('User not found by id {}'.format(user_id))
    else:
        db.execute('UPDATE user SET user_scope_uuid = ? WHERE id = ?',
                   (user_scope_uuid, user_id))

    db.commit()
    return user['id']


def find_user_by_id(id: int) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()


def find_user_by_email(email: str) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()


def find_user_by_amazon_id(amazon_id: str) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM user WHERE amazon_id = ?', (amazon_id,)).fetchone()


########################################################################
# THING model functions                                                #
########################################################################


def find_thing_by_endpoint_id_and_user_id(endpoint_id: str, user_id: int) -> sqlite3.Row:
    db = get_db()
    return db.execute('SELECT * FROM thing WHERE endpoint_id = ? and user_id = ?', (endpoint_id, user_id)).fetchone()


def find_things_by_user_id(user_id: int) -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('SELECT * FROM thing WHERE user_id = ?', (user_id,)).fetchall()


def find_thing_by_id(id: int) -> sqlite3.Row:
    db = get_db()
    return db.execute("""
        SELECT t.id, endpoint_id, user_id, friendly_name, description, manufacturer_name, 
            ac.id as alexa_category_id, ac.name as alexa_category_name 
        FROM thing t 
        INNER JOIN alexa_category ac ON ac.id = t.alexa_category_id 
        WHERE t.id = ?""", (id,)).fetchone()


def find_thing_capabilities_by_id(id: int) -> List[sqlite3.Row]:
    db = get_db()
    return db.execute("""
        SELECT tacp.thing_id, tacp.alexa_capability_id as id, tacp.properties, ac.name as name 
        FROM thing_alexa_capability_properties tacp 
        INNER JOIN alexa_capability ac ON ac.id = tacp.alexa_capability_id 
        WHERE tacp.thing_id = ?""", (id,)).fetchall()


def create_thing(endpoint_id: str, user_id: int, friendly_name: str, description: str, manufacturer_name: str,
                 alexa_category_id: int, alexa_capabilities_with_props: List[Tuple[str, str]]) -> int:
    db = get_db()
    db.execute("""
        INSERT INTO thing (endpoint_id, user_id, friendly_name, description, manufacturer_name, alexa_category_id) 
        VALUES (?, ?, ?, ?, ?, ?)""", (endpoint_id, user_id, friendly_name, description, manufacturer_name, alexa_category_id))
    thing_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    for acwp in alexa_capabilities_with_props:
        db.execute("""
            INSERT INTO thing_alexa_capability_properties (thing_id, alexa_capability_id, properties) 
            VALUES (?, ?, ?)""", (thing_id, acwp[0], acwp[1]))
    db.commit()
    return thing_id


def update_thing(id: int, endpoint_id: str, user_id: int, friendly_name: str, description: str, manufacturer_name: str,
                 alexa_category_id: int, alexa_capabilities_with_props: List[Tuple[str, str]]) -> int:
    db = get_db()
    db.execute("""
        UPDATE thing SET endpoint_id =?, user_id = ?, friendly_name = ?, description = ?, manufacturer_name = ?, alexa_category_id = ? 
        WHERE id = ?""", (endpoint_id, user_id, friendly_name, description, manufacturer_name, alexa_category_id, id))
    db.execute('DELETE FROM thing_alexa_capability_properties WHERE thing_id = ?', (id,))
    for acwp in alexa_capabilities_with_props:
        db.execute("""
            INSERT INTO thing_alexa_capability_properties (thing_id, alexa_capability_id, properties) 
            VALUES (?, ?, ?)""", (id, acwp[0], acwp[1]))
    db.commit()
    return id


def delete_thing(id: int) -> None:
    db = get_db()
    db.execute('DELETE FROM thing_alexa_capability_properties WHERE thing_id = ?', (id,))
    db.execute('DELETE FROM thing WHERE id = ?', (id,))
    db.commit()


########################################################################
# CATEGORY/CAPABILITY models functions                                 #
########################################################################


def get_all_categories() -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('SELECT id, name FROM alexa_category').fetchall()


def get_all_capabilities() -> List[sqlite3.Row]:
    db = get_db()
    return db.execute('SELECT id, name FROM alexa_capability').fetchall()
