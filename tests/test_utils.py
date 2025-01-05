import unittest
from unittest.mock import patch
from utils import get_host_name, format_scan_results, analyze_encrypted_traffic, detect_tls_handshake
import socket
class TestUtils(unittest.TestCase):

    @patch('utils.socket.gethostbyaddr')
    def test_get_host_name_valid_ip(self, mock_gethostbyaddr):
        # Mock successful host resolution
        mock_gethostbyaddr.return_value = ("example.com", [], [])
        result = get_host_name("8.8.8.8")
        self.assertEqual(result, "example.com")
        mock_gethostbyaddr.assert_called_once_with("8.8.8.8")

    @patch('utils.socket.gethostbyaddr')
    def test_get_host_name_invalid_ip(self, mock_gethostbyaddr):
        # Mock failure to resolve hostname
        mock_gethostbyaddr.side_effect = socket.herror
        result = get_host_name("999.999.999.999")
        self.assertIsNone(result)
        mock_gethostbyaddr.assert_called_once_with("999.999.999.999")

    def test_format_scan_results(self):
        # Test formatting of scan results
        scan_results = [
            ("192.168.1.1", 80, "open", "Apache/2.4.41"),
            ("192.168.1.2", 22, "closed", ""),
        ]
        expected_result = (
            "IP: 192.168.1.1, Port: 80, Status: open, Banner: Apache/2.4.41\n"
            "IP: 192.168.1.2, Port: 22, Status: closed, Banner: "
        )
        result = format_scan_results(scan_results)
        self.assertEqual(result, expected_result)

    def test_format_scan_results_empty(self):
        # Test formatting of empty scan results
        scan_results = []
        result = format_scan_results(scan_results)
        self.assertEqual(result, "")

    def test_analyze_encrypted_traffic(self):
        # Test the placeholder function for completeness
        # Since this is a placeholder, just ensure it doesn't raise errors
        try:
            analyze_encrypted_traffic(None)
        except Exception as e:
            self.fail(f"analyze_encrypted_traffic raised an unexpected exception: {e}")

    def test_detect_tls_handshake_valid(self):
        # Test detection of a TLS handshake with a valid packet
        packet = b'\x16\x03\x01\x02\x00'  # Example TLS handshake bytes
        result = detect_tls_handshake(packet)
        self.assertTrue(result)

    def test_detect_tls_handshake_invalid(self):
        # Test detection of a TLS handshake with an invalid packet
        packet = b'\x15\x01\x00\x01\x00'  # Example non-TLS bytes
        result = detect_tls_handshake(packet)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
