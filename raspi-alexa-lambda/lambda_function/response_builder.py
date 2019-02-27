import json
import logging
import uuid
from typing import Any, Dict, Union, List

from .error_type import ErrorType

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def build_auth_response() -> Dict[str, Any]:
    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Authorization",
                "name": "AcceptGrant.Response",
                "payloadVersion": "3",
                "messageId": _get_uuid(),
            },
            "payload": {}
        }
    }
    logger.debug("Alexa.Authorization Response: %s", json.dumps(response))
    return response


def build_discovery_response(endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    logger.debug("Alexa.Discovery Response: %s", json.dumps(response))
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
    logger.debug("Alexa.PowerController Response: %s", json.dumps(response))
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
    logger.debug("Alexa.InputController Response: %s", json.dumps(response))
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
    logger.debug("Alexa.InputController Response: %s", json.dumps(response))
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
    logger.debug("Alexa.ErrorResponse: %s", json.dumps(response))
    return response


def build_error_auth_response(error_type: ErrorType, error_message: str) -> Dict[str, Any]:
    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Authorization",
                "name": "ErrorResponse",
                "payloadVersion": "3",
                "messageId": _get_uuid(),
            },
            "payload": {
                "type": error_type.name,
                "message": error_message
            }
        }
    }
    logger.debug("Alexa.AuthErrorResponse: %s", json.dumps(response))
    return response


def build_error_common_response(error_type: ErrorType, error_message: str) -> Dict[str, Any]:
    response = {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "payloadVersion": "3",
                "messageId": _get_uuid(),
            },
            "payload": {
                "type": error_type.name,
                "message": error_message
            }
        }
    }
    logger.debug("Alexa.CommonErrorResponse: %s", json.dumps(response))
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
