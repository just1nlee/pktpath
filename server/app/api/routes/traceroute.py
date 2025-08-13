from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.services.traceroute_service import TracerouteService

router = APIRouter(prefix="/traceroute", tags=["traceroute"])

class TracerouteRequest(BaseModel):
    target: str

class TracerouteResponse(BaseModel):
    target: str
    hops: List[Dict]
    success: bool
    error: str = None

@router.post("/", response_model=TracerouteResponse)
async def run_traceroute(request: TracerouteRequest):
    """
    Run traceroute to a specified target
    """
    try:
        # Validate target
        if not request.target:
            raise HTTPException(status_code=400, detail="Target is required")
        
        # Run traceroute
        hops = TracerouteService.run_traceroute(request.target)
        
        # Check for errors
        if hops and len(hops) == 1 and "error" in hops[0]:
            return TracerouteResponse(
                target=request.target,
                hops=[],
                success=False,
                error=hops[0]["error"]
            )
        
        return TracerouteResponse(
            target=request.target,
            hops=hops,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "traceroute"}