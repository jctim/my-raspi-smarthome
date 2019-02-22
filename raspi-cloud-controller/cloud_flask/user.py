import logging

import requests
from flask import Blueprint
from flask import flash, g, redirect, render_template, request, session, url_for, current_app
from flask import logging as flask_logging

from . import db
from .common import AMAZON_PROFILE_REQUEST, AMAZON_TOKEN_REQUEST
from .common import load_logged_in_user, login_required, generate_uuid as _uuid

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(flask_logging.default_handler)
_LOGGER.setLevel(logging.DEBUG)

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.before_app_request
def before_app_request():
    load_logged_in_user()


@bp.route('/')
def thing_index():
    return redirect(url_for('user.profile'))


@bp.route('/login')
def login():
    return render_template('user/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


@bp.route('/handle_login')
def handle_login():
    request_args = request.args
    if 'error' in request_args:
        _LOGGER.debug('%s: %s', request_args['error'], request_args['error_description'])
        error = request_args['error_description']
    elif 'code' in request_args:
        code = request_args['code'],

        auth_code_response = requests.post(AMAZON_TOKEN_REQUEST, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': url_for('user.handle_login', _external=True, _scheme='https'),
            'client_id': current_app.config['AMAZON_CLIENT_ID'],
            'client_secret': current_app.config['AMAZON_CLIENT_SECRET']
        })
        auth_code_json = auth_code_response.json()

        if auth_code_response.status_code != 200:
            _LOGGER.debug('%s: %s', auth_code_json['error'], auth_code_json['error_description'])
            error = auth_code_json['error_description']
        else:
            auth_code_json = auth_code_response.json()
            access_token = auth_code_json['access_token']

            profile_response = requests.get(AMAZON_PROFILE_REQUEST.format(access_token))
            profile_json = profile_response.json()

            if profile_response.status_code != 200:
                _LOGGER.debug('%s: %s', profile_json['error'], profile_json['error_description'])
                error = profile_json['error_description']
            else:
                amazon_id = profile_json['user_id']
                email = profile_json['email']

                user_id = db.create_or_update_user(email, amazon_id)

                session.clear()
                session['user_id'] = user_id
                return redirect(url_for('user.profile'))

    else:
        error = 'Unknown response from Amazon: {}'.format(request_args)

    flash(error)
    return render_template('user/login.html')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':  # Generate only 'user scope' uuid
        user_id = g.user['id']
        db.update_user_scope_uuid(user_id, _uuid())
        g.user = db.find_user_by_id(user_id)  # refresh user with new 'user scope' for request
        return redirect(url_for('user.profile')) # avoid browser asking for re-submit form on refresh action

    return render_template('user/profile.html')
