"""
AI-related schemas for Kanban application.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


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


# Part 9: AI-Powered Kanban Operations Schemas

class ActionType(str, Enum):
    """
    Enum for AI action types on Kanban elements.
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    MOVE = "MOVE"
    DELETE = "DELETE"


class KanbanUpdate(BaseModel):
    """
    Schema for AI-generated Kanban updates.
    """
    action: ActionType = Field(..., description="Type of action to perform")
    element_type: Literal["board", "column", "card"] = Field(..., 
                                                               description="Type of element to update")
    element_id: Optional[int] = Field(None, description="ID of element to update (for UPDATE, MOVE, DELETE)")
    element_data: Optional[dict] = Field(None, description="Data for new/updated element (for CREATE, UPDATE)")
    target_column_id: Optional[int] = Field(None, description="Target column ID for MOVE actions")
    new_position: Optional[int] = Field(None, description="New position for MOVE actions")


class UserResponse(BaseModel):
    """
    Schema for AI text response to user.
    """
    text: str = Field(..., description="AI's text response to the user")
    explanation: Optional[str] = Field(None, description="Optional explanation of actions taken")


class AIKanbanResponse(BaseModel):
    """
    Complete response schema for AI Kanban operations.
    """
    user_response: UserResponse = Field(..., description="Text response to show user")
    kanban_updates: List[KanbanUpdate] = Field([], description="List of Kanban updates to apply")
    requires_confirmation: bool = Field(False, description="Whether updates require user confirmation")