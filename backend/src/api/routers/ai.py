"""
AI router for Kanban application.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.services.ai_service import openrouter_service
from src.schemas.ai import AIRequest, AIResponse, AITestResponse, AIHealthCheck
from src.api.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    dependencies=[Depends(HTTPBearer())],
)


@router.get("/test", response_model=AITestResponse)
async def test_ai_connection(
    current_user: dict = Depends(get_current_user)
) -> AITestResponse:
    """
    Test endpoint for AI connectivity.
    
    This endpoint sends a simple "2+2" question to the OpenRouter API
    and returns the response to verify that the AI service is working.
    """
    try:
        logger.info(f"User {current_user['username']} testing AI connection")
        
        # Test the connection
        success = await openrouter_service.test_connection()
        
        if success:
            # Get the actual response for the test
            messages = [{"role": "user", "content": "What is 2+2?"}]
            response = await openrouter_service.chat_completion(messages, max_tokens=10)
            
            return AITestResponse(
                success=True,
                message="AI service is working correctly",
                response=response,
                error=None
            )
        else:
            return AITestResponse(
                success=False,
                message="AI service test failed",
                response=None,
                error="Connection test returned false"
            )
            
    except Exception as e:
        logger.error(f"AI test endpoint failed: {e}")
        return AITestResponse(
            success=False,
            message="AI service test failed",
            response=None,
            error=str(e)
        )


@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(
    request: AIRequest,
    current_user: dict = Depends(get_current_user)
) -> AIResponse:
    """
    Chat with AI assistant.
    
    This endpoint sends a user message to the OpenRouter API
    and returns the AI response.
    """
    try:
        logger.info(f"User {current_user['username']} sending message to AI: {request.message[:50]}...")
        
        # Prepare messages for OpenRouter format
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        # Get AI response
        response = await openrouter_service.chat_completion(
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Calculate approximate token usage (simple estimation)
        # In production, this should come from the API response
        tokens_used = len(request.message.split()) + len(response.split())
        
        return AIResponse(
            response=response,
            model=openrouter_service.model,
            tokens_used=tokens_used,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"AI chat endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {str(e)}"
        )


@router.get("/health", response_model=AIHealthCheck)
async def ai_health_check(
    current_user: dict = Depends(get_current_user)
) -> AIHealthCheck:
    """
    Health check endpoint for AI service.
    
    This endpoint checks if the AI service is properly configured
    and can connect to the OpenRouter API.
    """
    try:
        logger.info(f"User {current_user['username']} checking AI health")
        
        # Test connection to OpenRouter
        api_connected = await openrouter_service.test_connection()
        
        return AIHealthCheck(
            status="healthy" if api_connected else "degraded",
            api_connected=api_connected,
            model=openrouter_service.model,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return AIHealthCheck(
            status="unhealthy",
            api_connected=False,
            model=openrouter_service.model,
            timestamp=datetime.utcnow()
        )