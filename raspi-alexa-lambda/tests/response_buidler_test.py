import json
import unittest
from unittest import mock

from endpoint_builder import build_discovery_endpoint
from response_builder import (build_discovery_response,
                              build_power_controller_response,
                              build_input_controller_response)


# TODO add more tests...

class ResponseBuilderTest(unittest.TestCase):

    @mock.patch('response_builder.uuid')
    def test_build_discovery_response(self, mock_uuid):
        mock_uuid.uuid4.return_value = '16120434-3e91-4b65-a2ee-f30cbb5fa1f6'

        with open('json/cloud-api-discovery-response-01.json') as f:
            cloud_api_discovery_endpoint = json.load(f)
        with open('json/alexa-discovery-response-01.json') as f:
            alexa_discovery_endpoint_expected = json.load(f)

        alexa_discovery_endpoint_response = build_discovery_response([
            build_discovery_endpoint(cloud_api_discovery_endpoint["endpoints"][0])
        ])
        self.assertEqual(alexa_discovery_endpoint_expected, alexa_discovery_endpoint_response)

    @mock.patch('response_builder.uuid')
    def test_build_power_controller_response(self, mock_uuid):
        mock_uuid.uuid4.return_value = '16120434-3e91-4b65-a2ee-f30cbb5fa1f6'
        correlation_token = 'd4ba89e1-cfc9-4734-bf3d-3fdf70535bed'
        time = '2019-02-24T12:50:00.00Z'

        with open('json/alexa-power-controller-response-ON.json') as f:
            alexa_power_controller_expected_on = json.load(f)

        with open('json/alexa-power-controller-response-OFF.json') as f:
            alexa_power_controller_expected_off = json.load(f)

        alexa_power_controller_response_on = build_power_controller_response("ON", time, correlation_token, endpoint_id='tv-01')
        self.assertEqual(alexa_power_controller_expected_on, alexa_power_controller_response_on)

        alexa_power_controller_response_off = build_power_controller_response("OFF", time, correlation_token, endpoint_id='tv-01')
        self.assertEqual(alexa_power_controller_expected_off, alexa_power_controller_response_off)

    @mock.patch('response_builder.uuid')
    def test_build_input_controller_response(self, mock_uuid):
        mock_uuid.uuid4.return_value = '16120434-3e91-4b65-a2ee-f30cbb5fa1f6'
        correlation_token = 'd4ba89e1-cfc9-4734-bf3d-3fdf70535bed'
        time = '2019-02-24T12:50:00.00Z'

        with open('json/alexa-input-controller-response-HDMI1.json') as f:
            alexa_input_controller_expected_hdmi1 = json.load(f)

        with open('json/alexa-input-controller-response-XBOX.json') as f:
            alexa_input_controller_expected_xbox = json.load(f)

        alexa_input_controller_response_hdmi1 = build_input_controller_response("HDMI 1", time, correlation_token, endpoint_id='tv-01')
        self.assertEqual(alexa_input_controller_expected_hdmi1, alexa_input_controller_response_hdmi1)

        alexa_input_controller_response_xbox = build_input_controller_response("XBOX", time, correlation_token, endpoint_id='tv-01')
        self.assertEqual(alexa_input_controller_expected_xbox, alexa_input_controller_response_xbox)
