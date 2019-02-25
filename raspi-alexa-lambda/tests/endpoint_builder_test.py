import unittest

from parameterized import parameterized

from endpoint_builder import build_discovery_endpoint


class EndpointBuilderTest(unittest.TestCase):

    @parameterized.expand([
        ['Alexa.EndpointHealth',
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['OTHER'],
             'capabilities': {'Alexa.EndpointHealth': ['connectivity']}
         },
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['OTHER'],
             'capabilities': [{
                 'interface': 'Alexa.EndpointHealth', 'type': 'AlexaInterface', 'version': '3',
                 'properties': {
                     'supported': [{'name': 'connectivity'}],
                     'proactivelyReported': True,
                     'retrievable': True
                 }
             }]
         }],
        ['Alexa.PowerController',
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['OTHER'],
             'capabilities': {'Alexa.PowerController': ['powerState']}
         },
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['OTHER'],
             'capabilities': [{
                 'interface': 'Alexa.PowerController', 'type': 'AlexaInterface', 'version': '3',
                 'properties': {
                     'supported': [{'name': 'powerState'}],
                     'proactivelyReported': True,
                     'retrievable': True
                 }
             }]
         }],
        ['Alexa.Speaker',
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['SPEAKER'],
             'capabilities': {'Alexa.Speaker': ['volume', 'muted']}
         },
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['SPEAKER'],
             'capabilities': [{
                 'interface': 'Alexa.Speaker', 'type': 'AlexaInterface', 'version': '3',
                 'properties': {
                     'supported': [{'name': 'volume'}, {'name': 'muted'}],
                     'proactivelyReported': True,
                     'retrievable': True
                 }
             }]
         }],
        ['Alexa.InputController',
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['TV'],
             'capabilities': {'Alexa.InputController': ['HDMI 1', 'HDMI 2', 'HDMI 3', 'HDMI 4']}
         },
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['TV'],
             'capabilities': [{
                 'interface': 'Alexa.InputController', 'type': 'AlexaInterface', 'version': '3',
                 'inputs': [{'name': 'HDMI 1'}, {'name': 'HDMI 2'}, {'name': 'HDMI 3'}, {'name': 'HDMI 4'}]
             }]
         }],
        ['Alexa.PlaybackController',
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['SPEAKER'],
             'capabilities': {'Alexa.PlaybackController': ['Play', 'Pause', 'Stop']}
         },
         {
             'endpointId': 'endpoint-01', 'friendlyName': 'Endpoint 01', 'description': 'Description', 'manufacturerName': 'Manufacturer',
             'displayCategories': ['SPEAKER'],
             'capabilities': [{
                 'interface': 'Alexa.PlaybackController', 'type': 'AlexaInterface', 'version': '3',
                 'supportedOperations': ['Play', 'Pause', 'Stop'],
             }]
         }]
    ])
    def test_build_discovery_endpoint(self, name, cloud_api_endpoint, expected_alexa_endpoint):
        actual_alexa_endpoint = build_discovery_endpoint(cloud_api_endpoint)
        self.assertEqual(expected_alexa_endpoint, actual_alexa_endpoint)
