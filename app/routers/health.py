from fastapi import APIRouter

router = APIRouter()

@router.get("", summary="Health check endpoint")
async def health_check():
    """
    Simple health check returning service status.
    """
    return {"status": "healthy"}