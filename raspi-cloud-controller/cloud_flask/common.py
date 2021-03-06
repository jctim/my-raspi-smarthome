import functools
import uuid

from flask import abort, g, redirect, session, url_for

from .db import find_thing_by_id, find_user_by_id

AMAZON_TOKEN_REQUEST = 'https://api.amazon.com/auth/o2/token'
AMAZON_PROFILE_REQUEST = 'https://api.amazon.com/user/profile?access_token={}'
ALEXA_CONTROL_TOPIC = 'alexa/{}/device/{}/control'
ALEXA_REPLY_TOPIC = 'alexa/{}/device/{}/reply'
DEV_USER_SCOPE = '_dev_scope_'


def load_logged_in_user():
    user_id = session.get('user_id')
    # user_id = 1  # TODO: for testing

    if user_id is None:
        g.user = None
    else:
        g.user = find_user_by_id(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))

        return view(**kwargs)

    return wrapped_view


def ensure_thing_belongs_to_user(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        thing_id = kwargs['thing_id']
        user_id = g.user['id']

        thing = find_thing_by_id(thing_id)
        if thing is None or thing['user_id'] != user_id:
            return abort(403)

        g.thing = thing
        return view(**kwargs)

    return wrapped_view


def generate_uuid() -> str:
    return str(uuid.uuid4())
