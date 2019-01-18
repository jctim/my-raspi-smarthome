import functools
import json
import time

import requests
from flask import Blueprint
from flask import current_app as app
from flask import (flash, g, jsonify, redirect, render_template, request,
                   session, url_for)

from .const import AMAZON_PROFILE_REQUEST, AMAZON_TOKEN_REQUEST, ALL_ENDPOINTS
from .db import find_user_by_amazon_id, find_things_by_user_id, find_thing_by_endpoint_id_and_user_id

bp = Blueprint('api', __name__, url_prefix='/api')

def ensure_amazon_user_id_exists(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        req_json = request.get_json()
        app.logger.debug('[ensure_amazon_user_id] json: ' + json.dumps(req_json))
        
        if 'accessToken' not in req_json:
            app.logger.debug('[ensure_amazon_user_id] access_token_not_provided')
            return jsonify({'error': 'access_token_not_provided'}), 400
        else:
            profile_response = requests.get(AMAZON_PROFILE_REQUEST + '?access_token=' + req_json['accessToken'])
            profile_json = profile_response.json()

            if profile_response.status_code != 200:
                app.logger.debug('[ensure_amazon_user_id] ' + profile_json['error'])
                return jsonify({'error': profile_json['error']}), 403
            else:
                amazon_user_id = profile_json['user_id']
                user = find_user_by_amazon_id(amazon_user_id)
                if user is None:
                    app.logger.debug('[ensure_amazon_user_id] user_not_found')
                    return jsonify({'error': 'user_not_found'}), 403
                else:
                    g.amazon_user_id = amazon_user_id
                    return view(**kwargs)

    return wrapped_view


def ensure_thing_related_to_user(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        req_json = request.get_json()
        app.logger.debug('[ensure_thing_related_to_user] json: ' + json.dumps(req_json))

        if 'endpointId' not in req_json:
            app.logger.debug('[ensure_thing_related_to_user] endpoint_id_not_provided')
            return jsonify({'error': 'endpoint_id_not_provided'}), 400
        else:
            app.logger.debug('[ensure_thing_related_to_user] AMAZON_USER_ID: ' + g.amazon_user_id)
            user = find_user_by_amazon_id(g.amazon_user_id)
            if user is None:
                app.logger.debug('[ensure_thing_related_to_user] user_not_found')
                return jsonify({'error': 'user_not_found'}), 403
            else:
                endpoint_id = req_json['endpointId']
                app.logger.debug('[ensure_thing_related_to_user] ENDPOINT_ID: ' + endpoint_id)
                user_thing = find_thing_by_endpoint_id_and_user_id(endpoint_id, user['id'])
                if user_thing is None:
                    app.logger.debug('[ensure_thing_related_to_user] thing_not_found')
                    return jsonify({'error': 'thing_not_found'}), 403
                else:
                    g.endpoint_id = endpoint_id
                    return view(**kwargs)

    return wrapped_view

@bp.route('/discover', methods=['POST'])
@ensure_amazon_user_id_exists
def discover():
    return jsonify({'endpoints': ALL_ENDPOINTS})  # TODO return all andpoints of the registered_user['devices_json']


@bp.route('/power/<command>', methods=['POST'])
@ensure_amazon_user_id_exists
@ensure_thing_related_to_user
def power(command):
    # TODO find pubnub key and call rpi-controller-api
    if command == 'TurnOn':
        result = 'ON'
    elif command == 'TurnOff':
        result = 'OFF'
    else:
        raise ValueError('Unsupported command: ' + command)

    return jsonify({'result': result, 'time': get_utc_timestamp()})


@bp.route('/input/<source>', methods=['POST'])
@ensure_amazon_user_id_exists
@ensure_thing_related_to_user
def input(source):
    # TODO find pubnub key and call rpi-controller-api
    result = source

    return jsonify({'result': result, 'time': get_utc_timestamp()})


def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))
