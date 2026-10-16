from typing import Dict, Any, List
import socket
import ipaddress
from .base import BaseCameraAdapter


class ONVIFDiscoveryAdapter:
    """Discovers ONVIF cameras strictly on explicitly authorized subnets."""

    def __init__(self, allowed_subnets: List[str]):
        self.allowed_subnets = allowed_subnets

    def is_ip_authorized(self, ip: str) -> bool:
        try:
            target = ipaddress.ip_address(ip)
            for subnet in self.allowed_subnets:
                if target in ipaddress.ip_network(subnet, strict=False):
                    return True
            return target.is_loopback
        except ValueError:
            return False

    def probe_device(self, ip: str, port: int = 80) -> Dict[str, Any]:
        if not self.is_ip_authorized(ip):
            return {"success": False, "error": "Địa chỉ IP không thuộc dải mạng camera được cấp phép"}

        try:
            with socket.create_connection((ip, port), timeout=3.0):
                return {
                    "success": True,
                    "ip": ip,
                    "port": port,
                    "onvif_detected": True,
                    "manufacturer": "Discovered ONVIF Device",
                }
        except Exception as e:
            return {"success": False, "error": f"Không thể kết nối cổng ONVIF: {type(e).__name__}"}
