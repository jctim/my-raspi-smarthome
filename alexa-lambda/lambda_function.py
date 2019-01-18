import json
import os

from botocore.vendored import requests

from endpoint_builder import *
from error_type import ErrorType
from response_builder import *

HOST = os.environ['HOST']

DISCOVERY_URL = HOST + '/api/discover'
POWER_URL = HOST + '/api/power/{0}'
INPUT_URL = HOST + '/api/input/{0}'


def lambda_handler(request, context):
    if request['directive']['header']['namespace'] == 'Alexa.Discovery' and (
            request['directive']['header']['name'] == 'Discover'):
        print("[DEBUG]", "Alexa.Discovery request",  json.dumps(request))
        return handle_discovery(request, context)
    elif request['directive']['header']['namespace'] == 'Alexa.PowerController' and (
            request['directive']['header']['name'] == 'TurnOn' or
            request['directive']['header']['name'] == 'TurnOff'):
        print("[DEBUG]", "Alexa.PowerController Request", json.dumps(request))
        return handle_power_control(request, context)
    elif request['directive']['header']['namespace'] == 'Alexa.InputController' and (
            request['directive']['header']['name'] == 'SelectInput'):
        print("[DEBUG]", "Alexa.InputController Request", json.dumps(request))
        return handle_input_control(request, context)
    else:
        print("[DEBUG]", "Unsupported Request", json.dumps(request))
        return build_error_response(ErrorType.INVALID_DIRECTIVE, 'Unsupported Operation',
                                    correlation_token=request['directive']['header']['correlationToken'],
                                    endpoint_id=request['directive']['endpoint']['endpointId'])


def handle_discovery(request, context):
    api_response = requests.post(DISCOVERY_URL, json={
        'messageId': request['directive']['header']['messageId'],
        'accessToken': request['directive']['payload']['scope']['token']
    })

    endpoints = []
    if api_response.status_code == 200 and 'endpoints' in api_response.json():
        all_endpoints = api_response.json()['endpoints']
        endpoints = [build_endpoint(endpoint) for endpoint in all_endpoints]

    return build_discovery_response(endpoints)


def handle_power_control(request, context):
    command = request['directive']['header']['name']
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
    else:
        api_json = api_response.json()
        return build_power_controller_response(api_json['result'], api_json['time'],
                                               correlation_token, endpoint_id)


def handle_input_control(request, context):
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
    else:
        api_json = api_response.json()
        return build_input_controller_response(api_json['result'], api_json['time'],
                                               correlation_token, endpoint_id)
