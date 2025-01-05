import unittest
from unittest.mock import patch, MagicMock
import argparse
from main import main

class TestMain(unittest.TestCase):

    @patch('main.scan_network')
    @patch('main.check_ip_abuseipdb')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_scan_ip(self, mock_args, mock_check_ip_abuseipdb, mock_scan_network):
        mock_args.return_value = argparse.Namespace(scan_ip="8.8.8.8", analyze=False, vuln_check=None)
        mock_scan_network.return_value = ['Device1', 'Device2']

        with patch('builtins.print') as mock_print:
            main()
            mock_scan_network.assert_called_once_with("8.8.8.8")
            mock_print.assert_any_call("Found devices: ['Device1', 'Device2']")

    @patch('main.assess_vulnerabilities')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_vuln_check(self, mock_args, mock_assess_vulnerabilities):
        mock_args.return_value = argparse.Namespace(scan_ip=None, analyze=False, vuln_check="nginx:1.16.1")
        mock_assess_vulnerabilities.return_value = [
            {'cve_id': 'CVE-2021-1234', 'description': 'Example vulnerability'}
        ]

        with patch('builtins.print') as mock_print:
            main()
            mock_assess_vulnerabilities.assert_called_once_with("nginx", "1.16.1")
            mock_print.assert_any_call('Vulnerability found: CVE-2021-1234 - Example vulnerability')

    @patch('main.scan_network')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_scan_ip_error(self, mock_args, mock_scan_network):
        mock_args.return_value = argparse.Namespace(scan_ip="999.999.999.999", analyze=False, vuln_check=None)
        mock_scan_network.side_effect = ValueError("Invalid IP address format: 999.999.999.999")

        with patch('builtins.print') as mock_print:
            main()
            mock_scan_network.assert_called_once_with("999.999.999.999")
            mock_print.assert_any_call("Invalid IP address format: 999.999.999.999")

    @patch('main.assess_vulnerabilities')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_vuln_check_invalid_format(self, mock_args, mock_assess_vulnerabilities):
        mock_args.return_value = argparse.Namespace(scan_ip=None, analyze=False, vuln_check="nginx1.16.1")

        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_any_call("Invalid format for --vuln-check. Use 'name:version'.")

    def test_scan_port_invalid_ip(self):
        from main import scan_network
        invalid_ip = "999.999.999.999"
        with self.assertRaises(ValueError) as context:
            scan_network(invalid_ip)
        self.assertIn("Invalid IP address format", str(context.exception))

if __name__ == "__main__":
    unittest.main()
