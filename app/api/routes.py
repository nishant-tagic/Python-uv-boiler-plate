from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/")
async def get_data(request: Request):
    """Example API endpoint"""
    return {
        "message": "This is protected data",
        "request_id": getattr(request.state, 'request_id', 'unknown'),
        "client_ip": getattr(request.state, 'client_ip', 'unknown')
    }

@router.post("/data")
async def create_data(request: Request, data: dict):
    """Example POST endpoint"""
    return {
        "message": "Data created successfully",
        "data": data,
        "request_id": getattr(request.state, 'request_id', 'unknown'),
    }
