import functools
import json
import logging
import time
import uuid
from queue import Queue, Empty
from typing import Tuple, Dict, Union, Optional, Any

import paho.mqtt.client as mqtt  # type: ignore
import requests
from flask import Blueprint
from flask import (g, jsonify, request)
from flask import logging as flask_logging

from . import db, mqtt_client
from .common import AMAZON_PROFILE_REQUEST, ALEXA_CONTROL_TOPIC, ALEXA_REPLY_TOPIC

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(flask_logging.default_handler)
_LOGGER.setLevel(logging.DEBUG)

bp = Blueprint('api', __name__, url_prefix='/api')


def api_ensure_amazon_user_id_exists(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        req_json = request.get_json()
        _LOGGER.debug('[ensure_amazon_user_id] json: %s', json.dumps(req_json))

        if 'accessToken' not in req_json:
            _LOGGER.debug('[ensure_amazon_user_id] access_token_not_provided')
            return jsonify({'error': 'access_token_not_provided'}), 400
        else:
            profile_response = requests.get(AMAZON_PROFILE_REQUEST.format(req_json['accessToken']))
            profile_json = profile_response.json()

            if profile_response.status_code != 200:
                _LOGGER.debug('[ensure_amazon_user_id] %s', profile_json['error'])
                return jsonify({'error': profile_json['error']}), 403
            else:
                amazon_user_id = profile_json['user_id']
                user = db.find_user_by_amazon_id(amazon_user_id)
                if user is None:
                    _LOGGER.debug('[ensure_amazon_user_id] user_not_found')
                    return jsonify({'error': 'user_not_found'}), 403
                else:
                    g.user_id = user['id']
                    g.amazon_user_id = amazon_user_id
                    return view(**kwargs)

    return wrapped_view


def api_ensure_thing_belongs_to_user(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        req_json = request.get_json()
        _LOGGER.debug('[ensure_thing_related_to_user] json: %s', json.dumps(req_json))

        if 'endpointId' not in req_json:
            _LOGGER.debug('[ensure_thing_related_to_user] endpoint_id_not_provided')
            return jsonify({'error': 'endpoint_id_not_provided'}), 400
        else:
            endpoint_id = req_json['endpointId']
            _LOGGER.debug('[ensure_thing_related_to_user] AMAZON_USER_ID: %s; USER_ID: %s; ENDPOINT_ID: %s',
                          g.amazon_user_id, g.user_id, endpoint_id)
            user_thing = db.find_thing_by_endpoint_id_and_user_id(endpoint_id, g.user_id)
            if user_thing is None:
                _LOGGER.debug('[ensure_thing_related_to_user] thing_not_found')
                return jsonify({'error': 'thing_not_found'}), 403
            else:
                g.endpoint_id = endpoint_id
                return view(**kwargs)

    return wrapped_view


@bp.route('/discover', methods=['POST'])
@api_ensure_amazon_user_id_exists
def discover():
    all_user_things = db.find_things_by_user_id(g.user_id)
    endpoints = [_build_endpoint(thing['id']) for thing in all_user_things]
    return jsonify({'endpoints': endpoints})


@bp.route('/power/<command>', methods=['POST'])
@api_ensure_amazon_user_id_exists
@api_ensure_thing_belongs_to_user
def power(command):
    (client, _) = _get_mqtt_client()

    if command == 'TurnOn':
        (_, _) = _send_control_message_async(g.endpoint_id, {'power': 'on'}, client=client)
        result = 'ON'  # TODO sync?
    elif command == 'TurnOff':
        (_, _) = _send_control_message_async(g.endpoint_id, {'power': 'off'}, client=client)
        result = 'OFF'  # TODO sync?
    else:
        return jsonify({'error': 'unsupported_command'}), 400

    return jsonify({'result': {'power': result}, 'time': _get_utc_timestamp()})


@bp.route('/input/<source>', methods=['POST'])
@api_ensure_amazon_user_id_exists
@api_ensure_thing_belongs_to_user
def input(source):
    (client, _) = _get_mqtt_client()

    (_, _) = _send_control_message_async(g.endpoint_id, {'source': source}, client=client)
    result = source  # TODO sync?

    return jsonify({'result': {'input': result}, 'time': _get_utc_timestamp()})


@bp.route('/speaker/<command>/<value>', methods=['POST'])
@api_ensure_amazon_user_id_exists
@api_ensure_thing_belongs_to_user
def speaker(command, value):
    (client, scope) = _get_mqtt_client()

    if command == 'SetVolume':
        result = _send_control_message_sync(g.endpoint_id, {'volume': value, 'type': 'abs'}, client=client)
    elif command == 'AdjustVolume':
        result = _send_control_message_sync(g.endpoint_id, {'volume': value, 'type': 'rel'}, client=client)
    elif command == 'SetMute':
        result = _send_control_message_sync(g.endpoint_id, {'volume': value, 'type': 'mute'}, client=client)
    else:
        return jsonify({'error': 'unsupported_command'}), 400

    if 'error' in result:
        return jsonify({'error': result['error']}), 500

    return jsonify({'result': {'volume': result['volume'], 'muted': result['muted']}, 'time': _get_utc_timestamp()})


def _send_control_message_async(endpoint_id: str, values: Dict[str, Union[str, int]], **kwargs) -> Optional[Tuple[mqtt.MQTTMessageInfo, str]]:
    m_uuid = str(kwargs.get('uuid') or _uuid())
    qos = int(kwargs.get('qos') or 2)
    client: mqtt.Client = kwargs.get('client')

    if client is not None:
        control_topic = ALEXA_CONTROL_TOPIC.format(endpoint_id)

        control_message = dict({"uuid": m_uuid}, **values)
        _LOGGER.debug('sending message %s', control_message)
        m_info = client.publish(control_topic, json.dumps(control_message), qos)
        return m_info, m_uuid

    return None


# TODO: add here async/await if possible
def _send_control_message_sync(endpoint_id: str, values: Dict[str, Union[str, int]], **kwargs) -> Optional[Dict[str, Union[str, int]]]:
    m_uuid = str(kwargs.get('uuid') or _uuid())
    qos = int(kwargs.get('qos') or 2)
    client: mqtt.Client = kwargs.get('client')
    q: Queue[Dict[str, Union[str, int]]] = Queue()

    def _on_message_inner(_client: mqtt.Client, _userdata: Any, message: mqtt.MQTTMessage) -> None:
        _LOGGER.debug('got message %s from topic %s', message.payload, message.topic)
        reply = json.loads(message.payload.decode("utf-8"))
        if 'uuid' not in reply or reply['uuid'] != m_uuid:
            return

        q.put(reply)

    if client is not None:
        control_topic = ALEXA_CONTROL_TOPIC.format(endpoint_id)
        reply_topic = ALEXA_REPLY_TOPIC.format(endpoint_id)

        client.subscribe(reply_topic)
        client.message_callback_add(reply_topic, _on_message_inner)

        control_message = dict({"uuid": m_uuid}, **values)
        _LOGGER.debug('sending message %s', control_message)
        client.publish(control_topic, json.dumps(control_message), qos).wait_for_publish()

        try:
            q_message = q.get(timeout=10)
        except Empty:
            _LOGGER.error("Got no reply at all")
            q_message = {'error': 'no reply from client'}

        client.message_callback_remove(reply_topic)
        client.unsubscribe(reply_topic)

        return q_message

    return None


def _build_endpoint(thing_id):
    thing = db.find_thing_by_id(thing_id)
    capabilities = db.find_thing_capabilities_by_id(thing_id)
    return {
        "endpointId": thing['endpoint_id'],
        "friendlyName": thing['friendly_name'],
        "description": thing['description'],
        "manufacturerName": thing['manufacturer_name'],
        "displayCategories": [
            thing['alexa_category_name']
        ],
        'capabilities': {capability['name']: [c.strip() for c in capability['properties'].split(',')] for capability in capabilities}
    }


def _get_mqtt_client() -> Tuple[mqtt.Client, str]:
    client = mqtt_client.get()
    mqtt_user_scope = db.get_user_mqtt_user_scope(g.user_id)

    return client, mqtt_user_scope


def _get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))


def _uuid() -> str:
    return str(uuid.uuid4())
