import functools
import json
import time

import requests
from flask import Blueprint
from flask import current_app as app
from flask import (flash, g, jsonify, redirect, render_template, request,
                   session, url_for)
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from . import db
from .common import AMAZON_PROFILE_REQUEST, AMAZON_TOKEN_REQUEST

bp = Blueprint('api', __name__, url_prefix='/api')


def api_ensure_amazon_user_id_exists(view):
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
                user = db.find_user_by_amazon_id(amazon_user_id)
                if user is None:
                    app.logger.debug('[ensure_amazon_user_id] user_not_found')
                    return jsonify({'error': 'user_not_found'}), 403
                else:
                    g.amazon_user_id = amazon_user_id
                    return view(**kwargs)

    return wrapped_view


def api_ensure_thing_belongs_to_user(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        req_json = request.get_json()
        app.logger.debug('[ensure_thing_related_to_user] json: {}'.format(json.dumps(req_json)))

        if 'endpointId' not in req_json:
            app.logger.debug('[ensure_thing_related_to_user] endpoint_id_not_provided')
            return jsonify({'error': 'endpoint_id_not_provided'}), 400
        else:
            app.logger.debug('[ensure_thing_related_to_user] AMAZON_USER_ID: {}'.format(g.amazon_user_id))
            user = db.find_user_by_amazon_id(g.amazon_user_id)
            if user is None:
                app.logger.debug('[ensure_thing_related_to_user] user_not_found')
                return jsonify({'error': 'user_not_found'}), 403
            else:
                user_id = user['id']
                endpoint_id = req_json['endpointId']
                app.logger.debug('[ensure_thing_related_to_user] ENDPOINT_ID: {}'.format(endpoint_id))
                user_thing = db.find_thing_by_endpoint_id_and_user_id(endpoint_id, user_id)
                if user_thing is None:
                    app.logger.debug('[ensure_thing_related_to_user] thing_not_found')
                    return jsonify({'error': 'thing_not_found'}), 403
                else:
                    g.user_id = user_id
                    g.endpoint_id = endpoint_id
                    return view(**kwargs)

    return wrapped_view


@bp.route('/discover', methods=['POST'])
@api_ensure_amazon_user_id_exists
def discover():
    all_user_things = db.find_things_by_user_id(g.user_id)
    endpoints = [_build_endpoint(thing['id']) for thing in all_user_things]
    return jsonify({'endpoints': endpoints})


def _build_endpoint(thing_id):
    thing = db.find_thing_by_id(thing_id)
    interfaces = db.find_thing_interfaces_by_id(thing_id)
    return {
        "endpointId": thing['endpoint_id'],
        "friendlyName": thing['friendly_name'],
        "description": thing['description'],
        "manufacturerName": thing['manufacturer_name'],
        "displayCategories": [
            thing['alexa_category_name']
        ],
        'capabilities': {interface['name']: [c.strip() for c in interface['capabilities'].split(',')] for interface in interfaces}
    }


@bp.route('/power/<command>', methods=['POST'])
@api_ensure_amazon_user_id_exists
@api_ensure_thing_belongs_to_user
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
@api_ensure_amazon_user_id_exists
@api_ensure_thing_belongs_to_user
def input(source):
    pubnub = _create_pubnub()
    pubnub.publish().channel('alexa').message({"requester": "Alexa", "device": g.endpoint_id, "source": source}).sync()
    result = source

    return jsonify({'result': result, 'time': _get_utc_timestamp()})


def _create_pubnub():
    keys = db.get_user_pubnub_keys(g.user_id)

    pnconfig = PNConfiguration()
    pnconfig.publish_key = keys[0]
    pnconfig.subscribe_key = keys[1]
    pnconfig.ssl = True
    return PubNub(pnconfig)


def _get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))
