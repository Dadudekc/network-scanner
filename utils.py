import socket


def get_host_name(ip_address):
    """
    Get the host name from an IP address.
    """
    try:
        host_name, _, _ = socket.gethostbyaddr(ip_address)
        return host_name
    except socket.herror:
        return None


def format_scan_results(scan_results):
    """
    Format scan results for display.
    
    Args:
        scan_results (list of tuple): List containing scan result tuples.
            Each tuple contains (IP, Port, Status, Banner).
    
    Returns:
        str: Formatted string of scan results.
    """
    formatted_results = []
    for result in scan_results:
        # Handle cases where the banner is empty
        banner = result[3] if result[3] else ""
        formatted_results.append(
            f"IP: {result[0]}, Port: {result[1]}, Status: {result[2]}, Banner: {banner.strip()}"
        )
    return "\n".join(formatted_results)


def analyze_encrypted_traffic(packet):
    """
    Analyze encrypted traffic patterns to infer activity without decrypting content.
    
    Parameters:
        packet (bytes): Raw packet data.

    Returns:
        str: Classification or description of the encrypted traffic.
    """
    # Define heuristic checks for common patterns
    try:
        # TLS Handshake detection (e.g., based on initial bytes)
        if packet.startswith(b'\x16\x03'):
            return "TLS handshake detected"

        # Check for DNS-over-HTTPS (DoH) patterns
        if b"application/dns-message" in packet:
            return "Potential DNS-over-HTTPS (DoH) traffic"

        # Check for common VPN protocols (heuristic example for OpenVPN)
        if packet.startswith(b'\x00\x0e\x3c\x4a'):
            return "OpenVPN encrypted traffic"

        # Check for SSH traffic patterns
        if b"SSH" in packet[:50]:
            return "SSH traffic detected"

        # Default fallback for unclassified encrypted traffic
        return "Unclassified encrypted traffic pattern detected"
    
    except Exception as e:
        return f"Error during encrypted traffic analysis: {e}"



def detect_tls_handshake(packet):
    """
    Detect a TLS handshake in network traffic.
    
    Parameters:
        packet (bytes): Raw packet data.

    Returns:
        bool: True if a TLS handshake is detected, False otherwise.
    """
    # Detect TLS handshakes using known patterns.
    # For example: TLS handshake starts with 0x16 (Handshake) and 0x03 (TLS Version).
    if packet.startswith(b'\x16\x03'):
        return True
    return False


def scan_port(ip, port, timeout=1):
    """
    Scan a single port on a specified IP address.
    
    Parameters:
        ip (str): The target IP address.
        port (int): The port to scan.
        timeout (int): Timeout for the socket connection in seconds.

    Returns:
        bool: True if the port is open, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            return result == 0
    except socket.error:
        return False


def scan_ports(ip, port_range=(1, 1024), timeout=1):
    """
    Scan a range of ports on a specified IP address.
    
    Parameters:
        ip (str): The target IP address.
        port_range (tuple): The range of ports to scan as (start_port, end_port).
        timeout (int): Timeout for each socket connection in seconds.

    Returns:
        list of int: List of open ports.
    """
    open_ports = []
    for port in range(port_range[0], port_range[1] + 1):
        if scan_port(ip, port, timeout):
            open_ports.append(port)
    return open_ports


def resolve_ip_or_host(target):
    """
    Resolve a target IP or hostname to an IP address.
    
    Parameters:
        target (str): The target hostname or IP address.

    Returns:
        str: The resolved IP address, or the input if it is already an IP.
    """
    try:
        return socket.gethostbyname(target)
    except socket.error:
        return None


def banner_grab(ip, port, timeout=1):
    """
    Attempt to grab a service banner from a specific port.
    
    Parameters:
        ip (str): The target IP address.
        port (int): The target port.
        timeout (int): Timeout for the connection in seconds.

    Returns:
        str: The grabbed banner, or an empty string if none is retrieved.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
            response = sock.recv(1024)
            return response.decode("utf-8", errors="ignore").strip()
    except socket.error:
        return ""


# Add additional utility functions as needed for your project.
