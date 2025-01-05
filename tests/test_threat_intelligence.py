import unittest
from unittest.mock import patch
from threat_intelligence import check_ip_abuseipdb
import requests

class TestThreatIntelligence(unittest.TestCase):

    @patch('threat_intelligence.requests.get')
    def test_valid_ip(self, mock_get):
        # Simulate a successful API response
        mock_response = {
            'data': {
                'abuseConfidenceScore': 42,
                'ipAddress': '8.8.8.8',
                'isPublic': True
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
        self.assertTrue(result['isPublic'])

    @patch('threat_intelligence.requests.get')
    def test_invalid_ip(self, mock_get):
        # Simulate a 400 Bad Request response for an invalid IP
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {
            "errors": [{"detail": "Invalid IP address."}]
        }

        # Call the function
        result = check_ip_abuseipdb('invalid-ip')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_missing_api_key(self, mock_get):
        # Simulate a 401 Unauthorized response due to missing API key
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {
            "errors": [{"detail": "Invalid API key."}]
        }

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_server_error(self, mock_get):
        # Simulate a 500 Internal Server Error response
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {
            "errors": [{"detail": "Internal server error."}]
        }

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_connection_error(self, mock_get):
        # Simulate a network connection error
        mock_get.side_effect = requests.ConnectionError

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

    @patch('threat_intelligence.requests.get')
    def test_empty_response(self, mock_get):
        # Simulate a 200 OK response with empty data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": None}

        # Call the function
        result = check_ip_abuseipdb('8.8.8.8')

        # Assertions
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
