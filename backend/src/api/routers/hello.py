"""
Hello world endpoints for testing and demonstration.
"""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/")
async def hello_world():
    """
    Simple hello world endpoint.
    
    Returns:
        dict: Greeting message
    """
    return {"message": "Hello, World!"}


@router.get("/{name}")
async def hello_name(name: str):
    """
    Personalized hello endpoint.
    
    Args:
        name: Name to greet
        
    Returns:
        dict: Personalized greeting
    """
    return {"message": f"Hello, {name}!"}


@router.get("/echo/{message}")
async def echo_message(
    message: str,
    repeat: Optional[int] = Query(1, ge=1, le=10, description="Number of times to repeat"),
):
    """
    Echo a message with optional repetition.
    
    Args:
        message: Message to echo
        repeat: Number of times to repeat the message
        
    Returns:
        dict: Echoed message
    """
    echoed = " ".join([message] * repeat)
    return {
        "original": message,
        "echoed": echoed,
        "repeat_count": repeat,
    }


@router.post("/echo")
async def echo_post(message: str):
    """
    Echo a message via POST request.
    
    Args:
        message: Message to echo
        
    Returns:
        dict: Echoed message with request info
    """
    return {
        "method": "POST",
        "message": message,
        "received_at": "now",  # In production, use datetime
    }