import IP2Location
import requests
import time
from typing import Dict, Optional
from pathlib import Path

class GeolocationService:
    """
    Hybrid geolocation service using ip-api.com first, then IP2Location database fallback.
    """
    
    _database = None
    _db_path = None
    _cache = {}
    _last_api_request_time = 0
    _api_rate_limit_delay = 0.1  # 100ms between API requests
    
    @classmethod
    def initialize(cls, db_path: str = None):
        """
        Initialize the geolocation service with IP2Location database.
        """
        if db_path:
            cls._db_path = db_path
        else:
            # Look for IP2Location database in data directory
            cls._db_path = Path(__file__).parent.parent.parent / "data" / "IP2LOCATION-LITE-DB5.IPV6.BIN"
            
            # If not found, try alternative names
            if not cls._db_path.exists():
                possible_names = [
                    "IP2LOCATION-LITE-DB5.BIN",
                    "DB5LITE.BIN",
                    "IP2LOCATION-LITE-DB11.BIN",
                    "IP2LOCATION-LITE-DB3.BIN"
                ]
                
                for name in possible_names:
                    test_path = Path(__file__).parent.parent.parent / "data" / name
                    if test_path.exists():
                        cls._db_path = test_path
                        print(f"Found database: {cls._db_path}")
                        break
        
        if not cls._db_path.exists():
            print(f"Warning: IP2Location database not found at {cls._db_path}")
            print("Will use ip-api.com only")
            cls._database = None
            return
        
        try:
            # Initialize IP2Location database
            cls._database = IP2Location.IP2Location()
            cls._database.open(str(cls._db_path))
            print(f"IP2Location database loaded successfully from {cls._db_path}")
        except Exception as e:
            print(f"Warning: Failed to load IP2Location database: {e}")
            print("Will use ip-api.com only")
            cls._database = None
    
    @classmethod
    def _is_private_ip(cls, ip_address: str) -> bool:
        """
        Check if an IP address is private/internal.
        """
        try:
            parts = ip_address.split('.')
            if len(parts) != 4:
                return False
            
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            # Private IP ranges
            if first_octet == 10:
                return True
            elif first_octet == 172 and 16 <= second_octet <= 31:
                return True
            elif first_octet == 192 and second_octet == 168:
                return True
            elif first_octet == 127:
                return True
            
            return False
        except:
            return False
    
    @classmethod
    def _get_location_from_api(cls, ip_address: str) -> Optional[Dict]:
        """
        Get geolocation data from ip-api.com API.
        """
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - cls._last_api_request_time
            if time_since_last < cls._api_rate_limit_delay:
                time.sleep(cls._api_rate_limit_delay - time_since_last)
            
            # Make API request
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=3)
            cls._last_api_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    return {
                        "latitude": data.get("lat"),
                        "longitude": data.get("lon"),
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "postal_code": data.get("zip"),
                        "timezone": data.get("timezone"),
                        "isp": data.get("isp"),
                        "source": "ip-api"
                    }
            
            return None
            
        except Exception as e:
            print(f"API lookup error for {ip_address}: {e}")
            return None
    
    @classmethod
    def _get_location_from_database(cls, ip_address: str) -> Optional[Dict]:
        """
        Get geolocation data from IP2Location database.
        """
        if not cls._database:
            return None
        
        try:
            # Query the IP2Location database
            record = cls._database.get_all(ip_address)
            
            # Check if we got valid data
            if record.country_short == "-" or record.country_short == "":
                return None
            
            # Extract data from the record
            return {
                "latitude": record.latitude,
                "longitude": record.longitude,
                "country": record.country_long,
                "country_code": record.country_short,
                "city": record.city,
                "region": record.region,
                "postal_code": None,  # IP2Location LITE doesn't include postal codes
                "timezone": None,     # IP2Location LITE doesn't include timezone
                "isp": None,          # IP2Location LITE doesn't include ISP
                "source": "ip2location-database"
            }
            
        except Exception as e:
            print(f"Database lookup error for {ip_address}: {e}")
            return None
    
    @classmethod
    def get_location(cls, ip_address: str) -> Dict:
        """
        Get geolocation data for an IP address using API first, then database fallback.
        """
        # Check if it's a private IP
        if cls._is_private_ip(ip_address):
            return {
                "latitude": None,
                "longitude": None,
                "country": None,
                "country_code": None,
                "city": None,
                "region": None,
                "postal_code": None,
                "timezone": None,
                "isp": None,
                "source": "private-ip"
            }
        
        # Check cache first
        if ip_address in cls._cache:
            return cls._cache[ip_address]
        
        # Try API first (better data quality)
        api_result = cls._get_location_from_api(ip_address)
        if api_result:
            cls._cache[ip_address] = api_result
            return api_result
        
        # Fallback to database (faster, but less accurate)
        db_result = cls._get_location_from_database(ip_address)
        if db_result:
            cls._cache[ip_address] = db_result
            return db_result
        
        # If both fail, return error
        result = {
            "latitude": None,
            "longitude": None,
            "country": None,
            "country_code": None,
            "city": None,
            "region": None,
            "postal_code": None,
            "timezone": None,
            "isp": None,
            "source": "both-sources-failed"
        }
        cls._cache[ip_address] = result
        return result
    
    @classmethod
    def clear_cache(cls):
        """Clear the cache"""
        cls._cache.clear()
    
    @classmethod
    def close(cls):
        """Close the database to free resources"""
        if cls._database:
            cls._database.close()
            cls._database = None
        # Rate limiting (very minimal)
        current_time = time.time()
        time_since_last = current_time - cls._last_request_time
        if time_since_last < cls._rate_limit_delay:
            time.sleep(cls._rate_limit_delay - time_since_last)
        
        try:
            # Make API request
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=3)
            cls._last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    result = {
                        "latitude": data.get("lat"),
                        "longitude": data.get("lon"),
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "postal_code": data.get("zip"),
                        "timezone": data.get("timezone"),
                        "isp": data.get("isp"),
                        "source": "ip-api"
                    }
                else:
                    result = {
                        "latitude": None,
                        "longitude": None,
                        "country": None,
                        "country_code": None,
                        "city": None,
                        "region": None,
                        "postal_code": None,
                        "timezone": None,
                        "isp": None,
                        "source": "ip-api-error"
                    }
            else:
                result = {
                    "latitude": None,
                    "longitude": None,
                    "country": None,
                    "country_code": None,
                    "city": None,
                    "region": None,
                    "postal_code": None,
                    "timezone": None,
                    "isp": None,
                    "source": "ip-api-error"
                }
            
            # Cache the result
            cls._cache[ip_address] = result
            return result
            
        except Exception as e:
            result = {
                "latitude": None,
                "longitude": None,
                "country": None,
                "country_code": None,
                "city": None,
                "region": None,
                "postal_code": None,
                "timezone": None,
                "isp": None,
                "source": "ip-api-error"
            }
            cls._cache[ip_address] = result
            return result