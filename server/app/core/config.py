from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "PktPath API"
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",  # Your Next.js frontend
        "http://127.0.0.1:3000",
    ]
    
    # Traceroute Configuration
    max_hops: int = 30
    timeout: int = 3
    command_timeout: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()