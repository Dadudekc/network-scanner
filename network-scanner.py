from scapy.all import ARP, Ether, srp
import socket
import concurrent.futures
from utils import get_host_name, format_scan_results
from threat_intelligence import check_ip_abuseipdb
from anomaly_detection import analyze_traffic

def scan_network(ip_range):
    """
    Scans the network using ARP requests to discover active devices.
    """
    print(f"Scanning network for active devices in range: {ip_range}")
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered, unanswered = srp(arp_request_broadcast, timeout=1, verbose=False)
    
    devices = []
    for sent, received in answered:
        device_info = {'ip': received.psrc, 'mac': received.hwsrc, 'host_name': get_host_name(received.psrc)}
        # Threat intelligence check
        threat_info = check_ip_abuseipdb(received.psrc)
        if threat_info:
            device_info['threat_info'] = threat_info
        devices.append(device_info)
    return devices

def scan_ports_on_device(ip, port_range=(1, 1025)):
    """
    Scans a range of ports on a specific device.
    """
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        scan_results = list(executor.map(lambda port: scan_port(ip, port), range(port_range[0], port_range[1]+1)))
    
    for port, is_open in zip(range(port_range[0], port_range[1]+1), scan_results):
        if is_open:
            open_ports.append(port)
    return open_ports

def scan_port(ip, port):
    """
    Attempts to connect to a given IP and port; returns True if the port is open.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if result == 0:
                return True
            else:
                return False
    except socket.error:
        return False

def main():
    ip_range = "192.168.1.1/24"  # Example IP range, customize as needed
    devices = scan_network(ip_range)
    for device in devices:
        print(f"Found device - IP: {device['ip']}, MAC: {device['mac']}, Hostname: {device.get('host_name', 'N/A')}")
        if 'threat_info' in device:
            print(f"\tThreat Info: {device['threat_info']}")
        open_ports = scan_ports_on_device(device['ip'])
        if open_ports:
            print(f"\tOpen ports on {device['ip']}: {', '.join(map(str, open_ports))}")
            # Here you could integrate the anomaly detection on traffic to/from this IP.
        else:
            print(f"\tNo open ports found on {device['ip']}.")

if __name__ == "__main__":
    main()
