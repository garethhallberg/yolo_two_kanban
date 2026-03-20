"""
AI-related schemas for Kanban application.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AIRequest(BaseModel):
    """
    Request schema for AI chat endpoint.
    """
    message: str = Field(..., min_length=1, max_length=1000, 
                         description="User message to send to AI")
    max_tokens: Optional[int] = Field(100, ge=10, le=500, 
                                     description="Maximum tokens for AI response")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, 
                                       description="Temperature for response creativity")


class AIResponse(BaseModel):
    """
    Response schema for AI chat endpoint.
    """
    response: str = Field(..., description="AI response content")
    model: str = Field(..., description="AI model used")
    tokens_used: int = Field(..., description="Number of tokens used")
    timestamp: datetime = Field(..., description="Response timestamp")


class AITestResponse(BaseModel):
    """
    Response schema for AI test endpoint.
    """
    success: bool = Field(..., description="Whether test was successful")
    message: str = Field(..., description="Test result message")
    response: Optional[str] = Field(None, description="AI response if successful")
    error: Optional[str] = Field(None, description="Error message if failed")


class AIHealthCheck(BaseModel):
    """
    Response schema for AI health check endpoint.
    """
    status: str = Field(..., description="Service status")
    api_connected: bool = Field(..., description="Whether OpenRouter API is reachable")
    model: str = Field(..., description="Configured AI model")
    timestamp: datetime = Field(..., description="Health check timestamp")