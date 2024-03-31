import socket
import concurrent.futures
from scapy.all import ARP, Ether, srp
import argparse

def scan_network(ip_range):
    print(f"Scanning network: {ip_range}")
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    
    devices = []
    for sent, received in answered_list:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    return devices

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            conn_result = s.connect_ex((ip, port))
            if conn_result == 0:
                try:
                    s.send(b'WhoAreYou\r\n')
                    banner = s.recv(100).decode().strip()
                except:
                    banner = "No Banner"
                return ip, port, "Open", banner
            else:
                return ip, port, "Closed", ""
    except socket.error as e:
        return ip, port, "Error", str(e)

def scan_ports(ip_address, port_range):
    ports = list(range(port_range[0], port_range[1] + 1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        scan_results = executor.map(lambda port: scan_port(ip_address, port), ports)
    
    open_ports = [result for result in scan_results if result[2] == "Open"]
    return open_ports

def main():
    parser = argparse.ArgumentParser(description="Network Scanner")
    parser.add_argument("--ip", help="Target IP or IP range (e.g., 192.168.1.1 or 192.168.1.0/24)")
    parser.add_argument("--ports", nargs=2, type=int, help="Port range to scan (e.g., 1 1024)")
    args = parser.parse_args()
    
    if args.ip and args.ports:
        devices = scan_network(args.ip)
        for device in devices:
            print(f"Found device at {device['ip']} with MAC {device['mac']}")
            for ip, port, status, banner in scan_ports(device['ip'], args.ports):
                print(f"\tPort {port}: {status} ({banner})")
    else:
        print("Please specify an IP range and port range to scan.")

if __name__ == "__main__":
    main()
