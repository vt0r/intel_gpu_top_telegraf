#!/usr/bin/env python3
"""
Tests for intel_gpu_top_telegraf.py
"""

import json
import unittest
from unittest.mock import patch, MagicMock

# Import the module to test
import intel_gpu_top_telegraf


class TestExecuteIntelGpuTop(unittest.TestCase):
    """Test cases for the execute_intel_gpu_top function"""

    def setUp(self):
        """Set up test fixtures"""
        self.valid_gpu_output = json.dumps([
            {
                "period": {
                        "duration": 52.312599,
                        "unit": "ms"
                },
                "frequency": {
                        "requested": 0.000000,
                        "actual": 0.000000,
                        "unit": "MHz"
                },
                "interrupts": {
                        "count": 0.000000,
                        "unit": "irq/s"
                },
                "rc6": {
                        "value": 100.000000,
                        "unit": "%"
                },
                "power": {
                        "GPU": 0.000000,
                        "Package": 4.172259,
                        "unit": "W"
                },
                "imc-bandwidth": {
                        "reads": 862.594740,
                        "writes": 72.741518,
                        "unit": "MiB/s"
                },
                "engines": {
                        "Render/3D": {
                                "busy": 0.000000,
                                "sema": 0.000000,
                                "wait": 0.000000,
                                "unit": "%"
                        },
                        "Blitter": {
                                "busy": 0.000000,
                                "sema": 0.000000,
                                "wait": 0.000000,
                                "unit": "%"
                        },
                        "Video": {
                                "busy": 0.000000,
                                "sema": 0.000000,
                                "wait": 0.000000,
                                "unit": "%"
                        },
                        "VideoEnhance": {
                                "busy": 0.000000,
                                "sema": 0.000000,
                                "wait": 0.000000,
                                "unit": "%"
                        }
                },
                "clients": {

                }
                }])

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    @patch('intel_gpu_top_telegraf.time.time_ns')
    def test_valid_output_injection(self, mock_time_ns, mock_sleep, mock_popen):
        """Test that timestamp and measurement_name are properly injected"""
        mock_time_ns.return_value = 1234567890

        # Setup mock process
        mock_process = MagicMock()
        mock_process.communicate.return_value = (self.valid_gpu_output, None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = intel_gpu_top_telegraf.execute_intel_gpu_top()
        result_dict = json.loads(result)

        # Verify timestamp and measurement_name were added
        self.assertIn('timestamp', result_dict)
        self.assertIn('measurement_name', result_dict)
        self.assertEqual(result_dict['timestamp'], 1234567890)
        self.assertEqual(result_dict['measurement_name'], 'intel_gpu_top')

        # Verify original data is preserved
        self.assertIn('period', result_dict)

        # Verify sleep was called (sampling interval)
        mock_sleep.assert_called_once_with(0.5)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    def test_empty_output(self, mock_sleep, mock_popen):
        """Test that empty output is handled correctly"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', None)
        mock_process.returncode = 0
        mock_process.args = ['intel_gpu_top', '-J']
        mock_popen.return_value = mock_process

        with self.assertRaises(SystemExit) as cm:
            intel_gpu_top_telegraf.execute_intel_gpu_top()

        self.assertEqual(cm.exception.code, 1)
        mock_sleep.assert_called_once_with(0.5)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    def test_nonzero_exit_code(self, mock_sleep, mock_popen):
        """Test that non-zero exit codes are handled correctly"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = (self.valid_gpu_output, 'Some error')
        mock_process.returncode = 1
        mock_process.args = ['intel_gpu_top', '-J']
        mock_popen.return_value = mock_process

        with self.assertRaises(SystemExit) as cm:
            intel_gpu_top_telegraf.execute_intel_gpu_top()

        self.assertEqual(cm.exception.code, 1)
        mock_sleep.assert_called_once_with(0.5)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    def test_invalid_json_output(self, mock_sleep, mock_popen):
        """Test that invalid JSON is handled correctly"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('not valid json', None)
        mock_process.returncode = 0
        mock_process.args = ['intel_gpu_top', '-J']
        mock_popen.return_value = mock_process

        with self.assertRaises(SystemExit) as cm:
            intel_gpu_top_telegraf.execute_intel_gpu_top()

        self.assertEqual(cm.exception.code, 1)
        mock_sleep.assert_called_once_with(0.5)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    def test_non_list_json_output(self, mock_sleep, mock_popen):
        """Test that non-list JSON is rejected"""
        invalid_output = json.dumps({"key": "value"})
        mock_process = MagicMock()
        mock_process.communicate.return_value = (invalid_output, None)
        mock_process.returncode = 0
        mock_process.args = ['intel_gpu_top', '-J']
        mock_popen.return_value = mock_process

        with self.assertRaises(SystemExit) as cm:
            intel_gpu_top_telegraf.execute_intel_gpu_top()

        self.assertEqual(cm.exception.code, 1)
        mock_sleep.assert_called_once_with(0.5)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    def test_empty_list_json_output(self, mock_sleep, mock_popen):
        """Test that empty list JSON is rejected"""
        invalid_output = json.dumps([])
        mock_process = MagicMock()
        mock_process.communicate.return_value = (invalid_output, None)
        mock_process.returncode = 0
        mock_process.args = ['intel_gpu_top', '-J']
        mock_popen.return_value = mock_process

        with self.assertRaises(SystemExit) as cm:
            intel_gpu_top_telegraf.execute_intel_gpu_top()

        self.assertEqual(cm.exception.code, 1)
        mock_sleep.assert_called_once_with(0.5)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    @patch('intel_gpu_top_telegraf.time.time_ns')
    def test_process_execution_parameters(self, mock_time_ns, mock_sleep, mock_popen):
        """Test that the process is executed with correct parameters"""
        mock_time_ns.return_value = 1234567890

        mock_process = MagicMock()
        mock_process.communicate.return_value = (self.valid_gpu_output, None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        intel_gpu_top_telegraf.execute_intel_gpu_top()

        # Verify Popen was called with correct arguments
        mock_popen.assert_called_once_with(['intel_gpu_top', '-J'], stdout=-1, text=True)

        # Verify sleep was called (sampling interval)
        mock_sleep.assert_called_once_with(0.5)

        # Verify SIGINT signal was sent
        mock_process.send_signal.assert_called_once_with(2)

        # Verify communicate was called with timeout
        mock_process.communicate.assert_called_once_with(timeout=3)

    @patch('intel_gpu_top_telegraf.subprocess.Popen')
    @patch('intel_gpu_top_telegraf.time.sleep')
    def test_output_is_valid_json(self, mock_sleep, mock_popen):
        """Test that output is always valid JSON"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = (self.valid_gpu_output, None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = intel_gpu_top_telegraf.execute_intel_gpu_top()

        # Verify result can be parsed as JSON
        try:
            parsed = json.loads(result)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

        # Verify sleep was called (sampling interval)
        mock_sleep.assert_called_once_with(0.5)


class TestLogging(unittest.TestCase):
    """Test cases for logging configuration"""

    def test_logger_exists(self):
        """Test that logger is properly initialized"""
        logger = intel_gpu_top_telegraf.logger
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'intel_gpu_top_telegraf.py')


if __name__ == '__main__':
    unittest.main()
