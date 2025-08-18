from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "pktpath API"
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",  # Your Next.js frontend
        "http://127.0.0.1:3000",
    ]
    
    # Traceroute Configuration - OPTIMIZED for better results
    max_hops: int = 15  # Reduced from 20 to avoid too many * responses
    timeout: int = 2    # Increased from 1 to give more time for responses
    command_timeout: int = 20  # Reduced from 30 for faster overall response
    
    class Config:
        env_file = ".env"

settings = Settings()