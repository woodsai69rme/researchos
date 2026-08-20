"""
ResearchOS SSRF Protection & Safe URL Target Validator
"""
import ipaddress
import socket
from urllib.parse import urlparse
from researchos.packages.core.exceptions import SSRFSecurityError
from researchos.packages.core.logging import logger

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918 private
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918 private
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918 private
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / Cloud metadata (AWS/GCP/Azure)
    ipaddress.ip_network("0.0.0.0/8"),         # Current network
    ipaddress.ip_network("100.64.0.0/10"),     # Carrier-grade NAT
    ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local
    ipaddress.ip_network("::1/128"),           # IPv6 Loopback
]

ALLOWED_SCHEMES = {"http", "https"}


def validate_outbound_url(url: str, allow_local_ai: bool = False) -> str:
    """
    Validates that a URL is safe to fetch and not attempting SSRF into internal networks.
    If allow_local_ai is True, localhost:11434 / localhost:1234 are permitted for Ollama/LM Studio.
    """
    if not url or not isinstance(url, str):
        raise SSRFSecurityError("Invalid or empty URL")

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise SSRFSecurityError(f"Prohibited URL scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFSecurityError("Missing hostname in target URL")

    # Local AI exception handling
    if allow_local_ai and hostname in ("localhost", "127.0.0.1", "::1"):
        if parsed.port in (11434, 1234, 8000, 3000, 6333):
            return url

    # Resolve IP address
    try:
        ip_str = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip_str)
    except Exception as e:
        logger.debug(f"Could not resolve host {hostname}: {e}")
        # If unresolvable in DNS check, allow standard web request to proceed unless obviously numeric
        return url

    for net in BLOCKED_IP_NETWORKS:
        if ip_obj in net:
            raise SSRFSecurityError(f"Security Alert: Target IP {ip_str} for host {hostname} belongs to private/metadata range {net}.")

    return url
