import IP2Location
from typing import Dict, Optional
from pathlib import Path

class GeolocationService:
    """
    Geolocation service using IP2Location LITE database.
    """
    
    _database = None
    _db_path = None
    
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
            raise FileNotFoundError(
                f"IP2Location database not found. Please download the BIN file and place it in the data directory. "
                f"Looked for: {cls._db_path}"
            )
        
        try:
            # Initialize IP2Location database
            cls._database = IP2Location.IP2Location()
            cls._database.open(str(cls._db_path))
            print(f"IP2Location database loaded successfully from {cls._db_path}")
        except Exception as e:
            raise Exception(f"Failed to load IP2Location database: {e}")
    
    @classmethod
    def get_location(cls, ip_address: str) -> Dict:
        """
        Get geolocation data for an IP address.
        """
        if not cls._database:
            raise Exception("GeolocationService not initialized. Call initialize() first.")
        
        try:
            # Query the IP2Location database
            record = cls._database.get_all(ip_address)
            
            # Check if we got valid data
            if record.country_short == "-" or record.country_short == "":
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
                    "source": "ip2location-lite-not-found"
                }
            
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
                "source": "ip2location-lite"
            }
            
        except Exception as e:
            print(f"IP2Location lookup error for {ip_address}: {e}")
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
                "source": "ip2location-lite-error"
            }
    
    @classmethod
    def close(cls):
        """Close the database to free resources"""
        if cls._database:
            cls._database.close()
            cls._database = None