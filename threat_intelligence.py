import requests
from config import ABUSE_IP_DB_API_KEY

def check_ip_abuseipdb(ip_address):
    url = f"https://api.abuseipdb.com/api/v2/check"
    headers = {
        'Accept': 'application/json',
        'Key': ABUSE_IP_DB_API_KEY
    }
    params = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90'
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        return None

# Example usage
if __name__ == "__main__":
    ip_address = "8.8.8.8"  # Example IP
    result = check_ip_abuseipdb(ip_address)
    if result:
        print(f"IP: {ip_address}, Abuse Confidence Score: {result['abuseConfidenceScore']}")
    else:
        print("Error or IP not found in AbuseIPDB.")
