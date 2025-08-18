import subprocess
import json
from typing import List, Dict, Optional
from app.core.config import settings
from app.services.geolocation_service import GeolocationService

class TracerouteService:
    @staticmethod
    def run_traceroute(target: str, include_geolocation: bool = True) -> List[Dict]:
        """
        Run traceroute command and return structured results with geolocation data
        """
        try:
            # Run traceroute command with optimized settings
            result = subprocess.run(
                [
                    "traceroute", 
                    "-n",  # Don't resolve hostnames
                    "-w", str(settings.timeout),  # Wait time per hop
                    "-m", str(settings.max_hops),  # Max hops
                    "-q", "1",  # Only 1 probe per hop (faster)
                    target
                ],
                capture_output=True,
                text=True,
                timeout=settings.command_timeout
            )
            
            # Check if traceroute command exists and works
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return [{"error": f"Traceroute failed: {error_msg}"}]
            
            # Parse traceroute output
            hops = []
            lines = result.stdout.strip().split('\n')
            
            # Skip the first line (header)
            for line in lines[1:]:
                if line.strip():
                    hop_data = TracerouteService._parse_hop_line(line)
                    if hop_data:
                        # Only add geolocation for valid IPs (not "*")
                        if include_geolocation and hop_data.get("ip") != "*":
                            geo_data = GeolocationService.get_location(hop_data["ip"])
                            hop_data["geolocation"] = geo_data
                            
                            # Convert string coordinates to numbers
                            lat = geo_data.get("latitude")
                            lng = geo_data.get("longitude")
                            
                            if lat is not None and lng is not None:
                                try:
                                    hop_data["lat"] = float(lat)
                                    hop_data["lng"] = float(lng)
                                except (ValueError, TypeError):
                                    hop_data["lat"] = None
                                    hop_data["lng"] = None
                            else:
                                hop_data["lat"] = None
                                hop_data["lng"] = None
                                
                        elif hop_data.get("ip") == "*":
                            # Add empty geolocation for "*" hops
                            hop_data["geolocation"] = {
                                "latitude": None,
                                "longitude": None,
                                "country": None,
                                "country_code": None,
                                "city": None,
                                "region": None,
                                "postal_code": None,
                                "timezone": None,
                                "isp": None,
                                "source": "no-response"
                            }
                            hop_data["lat"] = None
                            hop_data["lng"] = None
                        
                        hops.append(hop_data)
            
            # If no hops were parsed, return an error
            if not hops:
                return [{"error": "No traceroute data received"}]
            
            return hops
            
        except subprocess.TimeoutExpired:
            return [{"error": "Traceroute command timed out"}]
        except FileNotFoundError:
            return [{"error": "traceroute command not found. Please install traceroute."}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]
    
    @staticmethod
    def _parse_hop_line(line: str) -> Optional[Dict]:
        """
        Parse a single line of traceroute output
        """
        try:
            parts = line.split()
            if len(parts) < 2:
                return None
            
            hop_num = int(parts[0])
            ip_address = parts[1]
            
            # Handle cases where IP might be "*" (no response)
            if ip_address == "*":
                return {
                    "hop": hop_num,
                    "ip": "*",
                    "times": [None],
                    "hostname": None
                }
            
            # Extract response times if available
            times = []
            for part in parts[2:]:
                if part == '*':
                    times.append(None)
                elif part.replace('.', '').isdigit():
                    times.append(float(part))
            
            # If no times found, add a default
            if not times:
                times = [None]
            
            return {
                "hop": hop_num,
                "ip": ip_address,
                "times": times,
                "hostname": None
            }
        except (ValueError, IndexError):
            return None