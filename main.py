import argparse
import logging
import ipaddress
import numpy as np
from scapy.all import srp, Ether, ARP
from anomaly_detection import AnomalyDetectionModel
from threat_intelligence import check_ip_abuseipdb
from vulnerability_assessment import (
    initialize_database,
    fetch_vulnerability_data,
    assess_vulnerabilities,
)
from utils import scan_port, get_host_name, format_scan_results

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scan_network(ip_range):
    """
    Scan a network for active devices using ARP requests.
    Raises ValueError if the IP/network range is invalid.
    """
    # Validate IP
    try:
        ipaddress.ip_network(ip_range, strict=False)
    except ValueError:
        raise ValueError(f"Invalid IP address format: {ip_range}")

    logging.info(f"Scanning network range: {ip_range}")
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    for _, received in result:
        devices.append(received.psrc)
    logging.info(f"Found devices: {devices}")
    return devices

def scan_ports_on_device(ip, port_range=(1, 1024)):
    """
    Scan ports on a specific device.
    """
    logging.info(f"Scanning ports on {ip} within range {port_range}")
    open_ports = []
    for port in range(port_range[0], port_range[1] + 1):
        if scan_port(ip, port):
            open_ports.append(port)
    logging.info(f"Open ports on {ip}: {open_ports}")
    return open_ports

def main():
    """
    Main entry point for the Network Security Suite.
    """
    parser = argparse.ArgumentParser(description="Network Security Suite")
    parser.add_argument("--scan-ip", help="Scan a network IP range for devices (e.g., '192.168.1.0/24')")
    parser.add_argument("--analyze", action="store_true", help="Run anomaly detection on sample data")
    parser.add_argument("--vuln-check", help="Check vulnerabilities for a service (format: 'name:version')")
    args = parser.parse_args()

    # Initialize local vulnerability DB
    initialize_database()
    fetch_vulnerability_data()

    if args.scan_ip:
        try:
            devices = scan_network(args.scan_ip)
            print(f"Found devices: {devices}")
        except ValueError as e:
            print(str(e))

    if args.analyze:
        logging.info("Performing anomaly detection...")
        model = AnomalyDetectionModel(contamination=0.05)
        X_train = np.random.rand(100, 5)
        X_test = np.random.rand(10, 5)
        model.train(X_train)
        anomalies = model.predict(X_test)
        print(f"Anomalies detected at indices: {anomalies}")

    if args.vuln_check:
        try:
            service, version = args.vuln_check.split(":")
            logging.info(f"Checking vulnerabilities for {service} {version}")
            vulnerabilities = assess_vulnerabilities(service, version)
            for vuln in vulnerabilities:
                # Change print to match test expectation
                print(f"Vulnerability found: {vuln['cve_id']} - {vuln['description']}")
        except ValueError:
            print("Invalid format for --vuln-check. Use 'name:version'.")

if __name__ == "__main__":
    main()
