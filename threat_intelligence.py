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

NVD_API_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/1.0"

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


def assess_vulnerabilities(service_name_version):
    """
    Check known vulnerabilities for a given service and version using the NVD API.

    Args:
        service_name_version (str): Service name and version (e.g., 'nginx 1.16.1').

    Returns:
        list of dict: A list of vulnerabilities with details.
    """
    logging.info(f"Assessing vulnerabilities for: {service_name_version}")
    params = {
        'keyword': service_name_version,
        'resultsPerPage': 10,  # Limit the results to 10 for brevity
    }

    try:
        response = requests.get(NVD_API_BASE_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        if "result" in data and "CVE_Items" in data["result"]:
            vulnerabilities = []
            for item in data["result"]["CVE_Items"]:
                cve_id = item["cve"]["CVE_data_meta"]["ID"]
                description = item["cve"]["description"]["description_data"][0]["value"]
                vulnerabilities.append({"cve_id": cve_id, "description": description})
            logging.info(f"Found {len(vulnerabilities)} vulnerabilities for {service_name_version}.")
            return vulnerabilities
        else:
            logging.warning(f"No vulnerabilities found for {service_name_version}.")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error assessing vulnerabilities for {service_name_version}: {e}")
        return []
    except KeyError as e:
        logging.error(f"Unexpected response format from NVD API: {e}")
        return []


# Example usage
if __name__ == "__main__":
    # Example IP address check
    ip_address = "8.8.8.8"
    result = check_ip_abuseipdb(ip_address)
    if result:
        print(f"IP: {ip_address}, Abuse Confidence Score: {result.get('abuseConfidenceScore', 'N/A')}")
    else:
        print(f"Failed to fetch data for IP: {ip_address}. Check logs for details.")

    # Example vulnerability assessment
    service = "nginx 1.16.1"
    vulnerabilities = assess_vulnerabilities(service)
    for vuln in vulnerabilities:
        print(f"Vulnerability found: {vuln['cve_id']} - {vuln['description']}")
