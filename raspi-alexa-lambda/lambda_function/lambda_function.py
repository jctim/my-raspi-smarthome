import json
import logging
import os
from typing import Any, Dict, List

from .endpoint_builder import build_discovery_endpoint
from .error_type import ErrorType
from .response_builder import (build_auth_response,
                               build_discovery_response,
                               build_input_controller_response,
                               build_power_controller_response,
                               build_speaker_controller_response,
                               build_error_auth_response,
                               build_error_common_response,
                               build_error_response)

try:
    from botocore.vendored import requests  # type:ignore
except ImportError:
    import requests  # type:ignore

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

HOST = os.environ['HOST']

AUTH_URL = HOST + '{}/api/auth'
DISCOVERY_URL = HOST + '/api/discover'
POWER_URL = HOST + '/api/power/{0}'
INPUT_URL = HOST + '/api/input/{0}'
SPEAKER_URL = HOST + '/api/speaker/{0}/{1}'


# TODO: Reports - health etc.

def lambda_handler(request: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    request_namespace = request['directive']['header']['namespace']
    request_name = request['directive']['header']['name']
    logger.debug("%s request: %s", request_namespace, json.dumps(request))

    if request_namespace == 'Alexa.Authorization' and request_name == 'AcceptGrant':
        return handle_auth(request)

    if request_namespace == 'Alexa.Discovery' and request_name == 'Discover':
        return handle_discovery(request)

    if request_namespace == 'Alexa.PowerController' and (request_name == 'TurnOn' or
                                                         request_name == 'TurnOff'):
        return handle_power_control(request, request_name)

    if request_namespace == 'Alexa.InputController' and request_name == 'SelectInput':
        return handle_input_control(request, request_name)

    if request_namespace == 'Alexa.Speaker' and (request_name == 'SetVolume' or
                                                 request_name == 'AdjustVolume' or
                                                 request_name == 'SetMute'):
        return handle_speaker_control(request, request_name)

    logger.error("Unsupported Request")
    if 'correlationToken' in request['directive']['header'] and 'endpoint' in request['directive']:
        return build_error_response(ErrorType.INVALID_DIRECTIVE, 'Unsupported Operation',
                                    correlation_token=request['directive']['header']['correlationToken'],
                                    endpoint_id=request['directive']['endpoint']['endpointId'])

    return build_error_common_response(ErrorType.INTERNAL_ERROR, 'Unsupported Operation')


def handle_auth(request: Dict[str, Any]) -> Dict[str, Any]:
    api_response = requests.post(AUTH_URL, json={
        'messageId': request['directive']['header']['messageId'],
        'code': request['directive']['payload']['grant']['code'],
        'accessToken': request['directive']['payload']['grantee']['token']
    })

    if api_response.status_code != 200 or 'result' not in api_response.json():
        return build_error_auth_response(ErrorType.ACCEPT_GRANT_FAILED, 'Failed to handle the AcceptGrant directive...')

    return build_auth_response()


def handle_discovery(request: Dict[str, Any]) -> Dict[str, Any]:
    api_response = requests.post(DISCOVERY_URL, json={
        'messageId': request['directive']['header']['messageId'],
        'accessToken': request['directive']['payload']['scope']['token']
    })

    endpoints: List[Any] = []
    if api_response.status_code == 200 and 'endpoints' in api_response.json():
        endpoints = [build_discovery_endpoint(endpoint) for endpoint in api_response.json()['endpoints']]

    return build_discovery_response(endpoints)


def handle_power_control(request: Dict[str, Any], command: str) -> Dict[str, Any]:
    correlation_token = request['directive']['header']['correlationToken']
    endpoint_id = request['directive']['endpoint']['endpointId']

    api_response = requests.post(POWER_URL.format(command), json={
        'messageId': request['directive']['header']['messageId'],
        'endpointId': request['directive']['endpoint']['endpointId'],
        'accessToken': request['directive']['endpoint']['scope']['token']
    })

    if api_response.status_code != 200 or 'result' not in api_response.json():
        return build_error_response(ErrorType.ENDPOINT_UNREACHABLE, 'The device is unreachable',
                                    correlation_token, endpoint_id)

    api_json = api_response.json()
    return build_power_controller_response(api_json['result']['power'], api_json['time'],
                                           correlation_token, endpoint_id)


def handle_input_control(request: Dict[str, Any], _command: str) -> Dict[str, Any]:
    input_name = request['directive']['payload']['input']
    correlation_token = request['directive']['header']['correlationToken']
    endpoint_id = request['directive']['endpoint']['endpointId']

    api_response = requests.post(INPUT_URL.format(input_name), json={
        'messageId': request['directive']['header']['messageId'],
        'endpointId': request['directive']['endpoint']['endpointId'],
        'accessToken': request['directive']['endpoint']['scope']['token']
    })

    if api_response.status_code != 200 or 'result' not in api_response.json():
        return build_error_response(ErrorType.ENDPOINT_UNREACHABLE, 'The device is unreachable',
                                    correlation_token, endpoint_id)

    api_json = api_response.json()
    return build_input_controller_response(api_json['result']['input'], api_json['time'],
                                           correlation_token, endpoint_id)


def handle_speaker_control(request: Dict[str, Any], command: str) -> Dict[str, Any]:
    if 'volume' in request['directive']['payload']:
        value = request['directive']['payload']['volume']
    elif 'mute' in request['directive']['payload']:
        value = request['directive']['payload']['mute']
    else:
        value = None
    correlation_token = request['directive']['header']['correlationToken']
    endpoint_id = request['directive']['endpoint']['endpointId']

    api_response = requests.post(SPEAKER_URL.format(command, value), json={
        'messageId': request['directive']['header']['messageId'],
        'endpointId': request['directive']['endpoint']['endpointId'],
        'accessToken': request['directive']['endpoint']['scope']['token']
    })

    if api_response.status_code != 200 or 'result' not in api_response.json():
        return build_error_response(ErrorType.ENDPOINT_UNREACHABLE, 'The device is unreachable',
                                    correlation_token, endpoint_id)

    api_json = api_response.json()
    return build_speaker_controller_response(api_json['result']['volume'], api_json['result']['muted'], api_json['time'],
                                             correlation_token, endpoint_id)
