import unittest
from unittest.mock import patch
from threat_intelligence import check_ip_abuseipdb # Replace `your_module` with the actual file name
import requests

class TestCheckIPAbuseIPDB(unittest.TestCase):

    @patch('threat_intelligence.requests.get')
    def test_valid_ip(self, mock_get):
        # Simulate a successful API response
        mock_response = {
            'data': {
                'abuseConfidenceScore': 42,
                'ipAddress': '8.8.8.8'
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['abuseConfidenceScore'], 42)
        self.assertEqual(result['ipAddress'], '8.8.8.8')

    @patch('threat_intelligence.requests.get')
    def test_invalid_ip(self, mock_get):
        # Simulate an error response from the API
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {"errors": ["Invalid IP address"]}

        # Call the function
        result = check_ip_abuseipdb('invalid-ip')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_api_key_missing(self, mock_get):
        # Simulate an unauthorized response (e.g., missing or invalid API key)
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"errors": ["Invalid API key"]}

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_server_error(self, mock_get):
        # Simulate a server error response from the API
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"errors": ["Internal Server Error"]}

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_no_response(self, mock_get):
        # Simulate no response or connection error
        mock_get.side_effect = requests.ConnectionError

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
