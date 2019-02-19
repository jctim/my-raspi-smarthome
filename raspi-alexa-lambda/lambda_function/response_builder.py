import json
import uuid
from typing import Any, Dict, Union

from error_type import ErrorType


def build_discovery_response(endpoints: Dict[str, Any]) -> Dict[str, Any]:
    header = {
        "namespace": "Alexa.Discovery",
        "name": "Discover.Response",
        "payloadVersion": "3",
        "messageId": _get_uuid(),
    }
    response = {
        "event": {
            'header': header,
            'payload': {
                "endpoints": endpoints
            }
        }
    }
    print("[DEBUG]", "Alexa.Discovery Response:", json.dumps(response))
    return response


def build_power_controller_response(power_value: str, time: str,
                                    correlation_token: str, endpoint_id: str) -> Dict[str, Any]:
    response = {
        "context": {
            "properties": [_property('Alexa.PowerController', 'powerState', power_value, time)]
        },
        "event": {
            "header": _header(correlation_token),
            "endpoint": {
                "endpointId": endpoint_id
            },
            "payload": {}
        }
    }
    print("[DEBUG]", "Alexa.PowerController Response:", json.dumps(response))
    return response


def build_input_controller_response(input_value: str, time: str,
                                    correlation_token: str, endpoint_id: str) -> Dict[str, Any]:
    response = {
        "context": {
            "properties": [_property('Alexa.InputController', 'input', input_value, time)]
        },
        "event": {
            "header": _header(correlation_token),
            "endpoint": {
                "endpointId": endpoint_id
            },
            "payload": {}
        }
    }
    print("[DEBUG]", "Alexa.InputController Response:", json.dumps(response))
    return response


def build_speaker_controller_response(volume_value: str, muted_value: str, time: str,
                                      correlation_token: str, endpoint_id: str) -> Dict[str, Any]:
    response = {
        "context": {
            "properties": [
                _property('Alexa.Speaker', 'volume', volume_value, time),
                _property('Alexa.Speaker', 'muted', muted_value, time)
            ]
        },
        "event": {
            "header": _header(correlation_token),
            "endpoint": {
                "endpointId": endpoint_id
            },
            "payload": {}
        }
    }
    print("[DEBUG]", "Alexa.InputController Response:", json.dumps(response))
    return response


def build_error_response(error_type: ErrorType, error_message: str,
                         correlation_token: str, endpoint_id: str) -> Dict[str, Any]:
    response = {
        "event": {
            "header": _header(correlation_token, 'ErrorResponse'),
            "endpoint": {
                "endpointId": endpoint_id
            },
            "payload": {
                "type": error_type.name,
                "message": error_message
            }
        }
    }
    print("[DEBUG]", "Alexa.ErrorResponse:", json.dumps(response))
    return response


def _header(correlation_token: str, name: str = 'Response') -> Dict[str, str]:
    return {
        "namespace": "Alexa",
        "name": name,
        "payloadVersion": "3",
        "messageId": _get_uuid(),
        "correlationToken": correlation_token
    }


def _property(namespace: str, name: str, value: str, time: str) -> Dict[str, Union[str, int]]:
    return {
        "namespace": namespace,
        "name": name,
        "value": value,
        "timeOfSample": time,
        "uncertaintyInMilliseconds": 50
    }


def _get_uuid() -> str:
    return str(uuid.uuid4())
