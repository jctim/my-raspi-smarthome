import functools
import json
import time

import requests
from flask import Blueprint
from flask import current_app as app
from flask import (flash, g, jsonify, redirect, render_template, request,
                   session, url_for)

from .const import AMAZON_PROFILE_REQUEST, AMAZON_TOKEN_REQUEST
from .db import create_or_update_user, find_user_by_id, update_user_with_pubnub

bp = Blueprint('user', __name__, url_prefix='/user')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = find_user_by_id(user_id)


@bp.route('/login')
def login():
    return render_template('user/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


@bp.route('/handle_login')
def handle_login():
    error = None

    request_args = request.args
    if 'error' in request_args:
        app.logger.debug(request_args['error'] + ": " + request_args['error_description'])
        error = request_args['error_description']
    elif 'code' in request_args:
        code = request_args['code'],

        auth_code_response = requests.post(AMAZON_TOKEN_REQUEST, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': url_for('user.handle_login', _external=True, _scheme='https'),
            'client_id': app.config['AMAZON_CLIENT_ID'],
            'client_secret': app.config['AMAZON_CLIENT_SECRET']
        })
        auth_code_json = auth_code_response.json()

        if auth_code_response.status_code != 200:
            app.logger.debug(auth_code_json['error'] + ": " + auth_code_json['error_description'])
            error = auth_code_json['error_description']
        else:
            auth_code_json = auth_code_response.json()
            access_token = auth_code_json['access_token']

            profile_response = requests.get(AMAZON_PROFILE_REQUEST + '?access_token=' + access_token)
            profile_json = profile_response.json()

            if profile_response.status_code != 200:
                app.logger.debug(profile_json['error'] + ": " + profile_json['error_description'])
                error = profile_json['error_description']
            else:
                amazon_id = profile_json['user_id']
                email = profile_json['email']

                user_id = create_or_update_user(email, amazon_id)

                session.clear()
                session['user_id'] = user_id
                return redirect(url_for('user.profile'))

    else:
        error = 'Unknown response from Amazon: ' + request_args

    flash(error)
    return render_template('user/login.html')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        user_id = g.user['id']
        pubnub_publish_key = request.form['pubnub_publish_key']
        
        update_user_with_pubnub(user_id, pubnub_publish_key)
        g.user = find_user_by_id(user_id)

    return render_template('user/profile.html')
