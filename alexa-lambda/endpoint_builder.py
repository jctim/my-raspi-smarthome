import json
import uuid
from typing import Any, Dict

from error_type import ErrorType


def build_endpoint(endpoint):
    capabilities = [build_capability(cb, props) for cb, props in endpoint['capabilities'].items()]
    return {
        "endpointId": endpoint['endpointId'],
        "manufacturerName": endpoint['manufacturerName'],
        "friendlyName": endpoint['friendlyName'],
        "description": endpoint['description'],
        "displayCategories": endpoint['displayCategories'],
        "cookie": {
            # TODO
            "key1": "arbitrary key/value pairs for skill to reference this endpoint.",
                    "key2": "There can be multiple entries",
                    "key3": "but they should only be used for reference purposes.",
                    "key4": "This is not a suitable place to maintain current endpoint state."
        },
        "capabilities": capabilities
    }


def build_capability(cb, props):
    if cb == 'Alexa.PowerController' or cb == 'Alexa.Speaker' or cb == 'Alexa.EndpointHealth':
        return {
            "type": "AlexaInterface",
            "interface": cb,
            "version": "3",
            "properties": {
                "supported": [{'name':  prop} for prop in props],
                "proactivelyReported": True,
                "retrievable": True
            }
        }
    elif cb == 'Alexa.InputController':
        return {
            "type": "AlexaInterface",
            "interface": cb,
            "version": "3",
            "inputs": [{'name': prop} for prop in props]
        }
    elif cb == 'Alexa.PlaybackController':
        return {
            "type": "AlexaInterface",
            "interface": cb,
            "version": "3",
            "properties": {},
            "supportedOperations": [prop for prop in props],
            "proactivelyReported": True,
            "retrievable": True
        }
    else:
        return {
            "type": "AlexaInterface",
            "interface": cb,
            "version": "3"
        }
