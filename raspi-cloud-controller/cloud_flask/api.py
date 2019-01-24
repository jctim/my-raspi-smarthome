import functools
import json
import time

import requests

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

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
        app.logger.debug('[ensure_amazon_user_id] json: {}'.format(json.dumps(req_json)))

        if 'accessToken' not in req_json:
            app.logger.debug('[ensure_amazon_user_id] access_token_not_provided')
            return jsonify({'error': 'access_token_not_provided'}), 400
        else:
            profile_response = requests.get(AMAZON_PROFILE_REQUEST.format(req_json['accessToken']))
            profile_json = profile_response.json()

            if profile_response.status_code != 200:
                app.logger.debug('[ensure_amazon_user_id] {}'.format(profile_json['error']))
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
        app.logger.debug('[ensure_thing_related_to_user] json: {}'.format(json.dumps(req_json)))

        if 'endpointId' not in req_json:
            app.logger.debug('[ensure_thing_related_to_user] endpoint_id_not_provided')
            return jsonify({'error': 'endpoint_id_not_provided'}), 400
        else:
            app.logger.debug('[ensure_thing_related_to_user] AMAZON_USER_ID: {}'.format(g.amazon_user_id))
            user = find_user_by_amazon_id(g.amazon_user_id)
            if user is None:
                app.logger.debug('[ensure_thing_related_to_user] user_not_found')
                return jsonify({'error': 'user_not_found'}), 403
            else:
                endpoint_id = req_json['endpointId']
                app.logger.debug('[ensure_thing_related_to_user] ENDPOINT_ID: {}'.format(endpoint_id))
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
    pubnub = _create_pubnub()
    if command == 'TurnOn':
        pubnub.publish().channel('alexa').message({"requester": "Alexa", "device": g.endpoint_id, "power": "on"}).sync()
        result = 'ON'
    elif command == 'TurnOff':
        pubnub.publish().channel('alexa').message({"requester": "Alexa", "device": g.endpoint_id, "power": "off"}).sync()
        result = 'OFF'
    else:
        return jsonify({'error': 'unsupported_command'}), 400

    return jsonify({'result': result, 'time': _get_utc_timestamp()})


@bp.route('/input/<source>', methods=['POST'])
@ensure_amazon_user_id_exists
@ensure_thing_related_to_user
def input(source):
    pubnub = _create_pubnub()
    pubnub.publish().channel('alexa').message({"requester": "Alexa", "device": g.endpoint_id, "source": source}).sync()
    result = source

    return jsonify({'result': result, 'time': _get_utc_timestamp()})


def _create_pubnub():
    pnconfig = PNConfiguration()
    pnconfig.publish_key = app.config['PUBNUB_PUB_KEY']
    pnconfig.subscribe_key = app.config['PUBNUB_SUB_KEY']
    pnconfig.ssl = True
    return PubNub(pnconfig)


def _get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))
