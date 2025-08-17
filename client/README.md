## Setup

1. Clone the repository
2. Download the IP2Location database:
   ```bash
   cd server/data
   # Download from: https://lite.ip2location.com/database/db5-ip-country-region-city-latitude-longitude
   # Choose: DB5.LITE IPV6-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE (BIN format)
   # Save as: IP2LOCATION-LITE-DB5.IPV6.BIN
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Start the server: `uvicorn main:app --reload`