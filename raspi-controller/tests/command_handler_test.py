import unittest
from unittest import mock
from unittest.mock import call
from tv_controller.command_handler import handle_control_command


class CommandHandlerTest(unittest.TestCase):

    @mock.patch('tv_controller.command_handler.os')
    def test_handle_control_command_power(self, mock_os):
        handle_control_command({'power': 'on'})
        mock_os.system.assert_called_with('echo "tx 10:04" | cec-client RPI -s -d 1')

        handle_control_command({'power': 'off'})
        mock_os.system.assert_called_with('echo "tx 10:36" | cec-client RPI -s -d 1')

    @mock.patch('tv_controller.command_handler.os')
    def test_handle_control_command_source_hdmi_numbers(self, mock_os):
        handle_control_command({'source': 'HDMI 1'})
        self.assertEqual(mock_os.system.call_args_list[-2:],
                         [call('echo "tx 1F:82:10:00" | cec-client RPI -s -d 1'),
                          call('echo "tx 1F:86:10:00" | cec-client RPI -s -d 1')])

        handle_control_command({'source': 'HDMI 2'})
        self.assertEqual(mock_os.system.call_args_list[-2:],
                         [call('echo "tx 1F:82:20:00" | cec-client RPI -s -d 1'),
                          call('echo "tx 1F:86:20:00" | cec-client RPI -s -d 1')])

        handle_control_command({'source': 'HDMI 3'})
        self.assertEqual(mock_os.system.call_args_list[-2:],
                         [call('echo "tx 1F:82:30:00" | cec-client RPI -s -d 1'),
                          call('echo "tx 1F:86:30:00" | cec-client RPI -s -d 1')])

        handle_control_command({'source': 'HDMI 4'})
        self.assertEqual(mock_os.system.call_args_list[-2:],
                         [call('echo "tx 1F:82:40:00" | cec-client RPI -s -d 1'),
                          call('echo "tx 1F:86:40:00" | cec-client RPI -s -d 1')])

    @mock.patch('tv_controller.command_handler.os')
    def test_handle_control_command_source_custom_names(self, mock_os):
        hdmi1_names = ['ANDROID', 'ANDROID TV', 'MIBOX']
        [handle_control_command({'source': source}) for source in hdmi1_names]
        self.assertEqual(mock_os.system.call_args_list[-len(hdmi1_names)*2:],
                         len(hdmi1_names) * [call('echo "tx 1F:82:10:00" | cec-client RPI -s -d 1'),
                                             call('echo "tx 1F:86:10:00" | cec-client RPI -s -d 1')])

        hdmi2_names = ['XBOX']
        [handle_control_command({'source': source}) for source in hdmi2_names]
        self.assertEqual(mock_os.system.call_args_list[-len(hdmi2_names)*2:],
                         len(hdmi2_names) * [call('echo "tx 1F:82:20:00" | cec-client RPI -s -d 1'),
                                             call('echo "tx 1F:86:20:00" | cec-client RPI -s -d 1')])

        hdmi3_names = ['APPLE', 'APPLE TV']
        [handle_control_command({'source': source}) for source in hdmi3_names]
        self.assertEqual(mock_os.system.call_args_list[-len(hdmi3_names)*2:],
                         len(hdmi3_names) * [call('echo "tx 1F:82:30:00" | cec-client RPI -s -d 1'),
                                             call('echo "tx 1F:86:30:00" | cec-client RPI -s -d 1')])

        hdmi4_names = ['RASPBERRY', 'RASPBERRY PI', 'CONTROLLER']
        [handle_control_command({'source': source}) for source in hdmi4_names]
        self.assertEqual(mock_os.system.call_args_list[-len(hdmi4_names)*2:],
                         len(hdmi4_names) * [call('echo "tx 1F:82:40:00" | cec-client RPI -s -d 1'),
                                             call('echo "tx 1F:86:40:00" | cec-client RPI -s -d 1')])
