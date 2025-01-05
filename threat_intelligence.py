# D:\network-scanner\threat_intelligence.py

import requests
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
ABUSE_IP_DB_API_KEY = os.getenv("ABUSE_IP_DB_API_KEY")

if not ABUSE_IP_DB_API_KEY:
    raise ValueError("Missing ABUSE_IP_DB_API_KEY. Please set it in the .env file.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ip_abuseipdb(ip_address):
    """
    Check an IP address against AbuseIPDB for reported malicious activity.

    Args:
        ip_address (str): The IP address to check.

    Returns:
        dict: The response data from AbuseIPDB if successful.
        None: If the request fails or the IP address is not found.
    """
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        'Accept': 'application/json',
        'Key': ABUSE_IP_DB_API_KEY
    }
    params = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        logging.info(f"IP {ip_address} checked successfully.")
        return data['data']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking IP {ip_address}: {e}")
        return None
    except KeyError:
        logging.error(f"Unexpected response format for IP {ip_address}.")
        return None

# Example usage
if __name__ == "__main__":
    ip_address = "8.8.8.8"  # Example IP address to check
    result = check_ip_abuseipdb(ip_address)
    if result:
        print(f"IP: {ip_address}, Abuse Confidence Score: {result.get('abuseConfidenceScore', 'N/A')}")
    else:
        print(f"Failed to fetch data for IP: {ip_address}. Check logs for details.")
