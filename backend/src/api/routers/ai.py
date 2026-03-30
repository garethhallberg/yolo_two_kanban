"""
AI router for Kanban application.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session
from src.services.ai_service import openrouter_service
from src.schemas.ai import AIRequest, AIResponse, AITestResponse, AIHealthCheck, AIKanbanResponse, ActionType
from src.api.routers.auth import get_current_user
from src.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["ai"],
    dependencies=[Depends(HTTPBearer())],
)


@router.get("/test", response_model=AITestResponse)
async def test_ai_connection(
    current_user=Depends(get_current_user)
) -> AITestResponse:
    """
    Test endpoint for AI connectivity.

    This endpoint sends a simple "2+2" question to the OpenRouter API
    and returns the response to verify that the AI service is working.
    """
    try:
        logger.info(f"User {current_user.username} testing AI connection")
        
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


@router.post("/chat", response_model=AIKanbanResponse)
async def chat_with_ai(
    request: AIRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AIKanbanResponse:
    """
    Chat with AI assistant for Kanban operations.

    This endpoint sends a user message to the OpenRouter API
    and returns a structured response that may include Kanban updates.
    """
    try:
        logger.info(f"User {current_user.username} sending message to AI: {request.message[:50]}...")

        # Get user's board for context
        from src.services.board_service import BoardService

        board = BoardService.get_board_with_columns_and_cards(db, current_user.id)
        
        # Serialize board state for AI context
        board_context = BoardService.serialize_board_for_ai(board) if board else {"error": "No board found"}
        
        # Prepare messages for OpenRouter format with context and prompt engineering
        system_prompt = """
You are an AI assistant helping with Kanban board management. 
Analyze the current board state and user request, then provide helpful responses.

Guidelines:
1. Always acknowledge the current board state
2. For requests to create/edit/move cards, provide clear confirmation
3. For complex requests, ask for clarification if needed
4. Keep responses concise and action-oriented
5. If making changes, explain what you'll do before doing it
6. Use structured JSON format when providing Kanban updates

Response format for Kanban updates:
{
  "user_response": {
    "text": "Your response to the user",
    "explanation": "Optional explanation of actions"
  },
  "kanban_updates": [
    {
      "action": "CREATE|UPDATE|MOVE|DELETE",
      "element_type": "board|column|card",
      "element_id": null,
      "element_data": {},
      "target_column_id": null,
      "new_position": null
    }
  ],
  "requires_confirmation": true/false
}
"""
        
        context_message = f"Current Kanban board state:\n{board_context}\n\nUser request: {request.message}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_message}
        ]
        
        # Get AI response
        response = await openrouter_service.chat_completion(
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Parse AI response for structured Kanban updates
        kanban_updates = []
        requires_confirmation = False
        
        try:
            # Try to parse structured response (for AI that returns JSON)
            import json
            if response.strip().startswith('{') and response.strip().endswith('}'):
                parsed_response = json.loads(response)
                if 'kanban_updates' in parsed_response:
                    # Validate and parse updates
                    from src.schemas.ai import KanbanUpdate
                    for update_data in parsed_response['kanban_updates']:
                        try:
                            update = KanbanUpdate(**update_data)
                            kanban_updates.append(update)
                        except Exception as e:
                            logger.warning(f"Invalid Kanban update format: {e}")
                    
                    requires_confirmation = parsed_response.get('requires_confirmation', False)
                    
                    # Use the text response from the structured format if available
                    if 'user_response' in parsed_response:
                        response_text = parsed_response['user_response'].get('text', response)
                        explanation = parsed_response['user_response'].get('explanation', None)
                    else:
                        response_text = response
                        explanation = None
                else:
                    response_text = response
                    explanation = None
            else:
                # Try to extract card movement from AI reasoning text
                import re
                try:
                    # Look for patterns like "card id X" and "column id Y"
                    card_id_pattern = r'card.*?id\s*(\d+)'
                    column_pattern = r'column.*?id\s*(\d+)'
                    
                    card_id_match = re.search(card_id_pattern, response, re.IGNORECASE)
                    column_matches = list(re.finditer(column_pattern, response, re.IGNORECASE))
                    
                    if card_id_match and len(column_matches) >= 2:
                        # Extract card movement details
                        card_id = int(card_id_match.group(1))
                        from_column_id = int(column_matches[0].group(1))
                        to_column_id = int(column_matches[1].group(1))
                        
                        # Create Kanban update as proper Pydantic model
                        from src.schemas.ai import KanbanUpdate
                        kanban_updates.append(KanbanUpdate(
                            action="MOVE",
                            element_type="card",
                            element_id=card_id,
                            element_data={},
                            target_column_id=to_column_id,
                            new_position=999
                        ))
                        
                        response_text = f"I will move card {card_id} from column {from_column_id} to column {to_column_id}"
                        explanation = "Extracted card movement from AI reasoning"
                    else:
                        response_text = response
                        explanation = None
                except Exception as e:
                    logger.warning(f"Failed to extract card movement from reasoning: {e}")
                    response_text = response
                    explanation = None
        except Exception as e:
            logger.warning(f"Failed to parse structured AI response: {e}")
            response_text = response
            explanation = None
        
        # Add fallback handling for malformed responses
        if not response_text or response_text.strip() == "":
            response_text = "I'm sorry, I couldn't process your request properly. Please try again."
            explanation = "The AI response was empty or malformed"
        
        elif len(response_text) > 5000:  # Very long response
            response_text = response_text[:5000] + "... (response truncated)"
            explanation = "The AI response was very long and has been truncated"
        
        # Store conversation history
        try:
            from src.database.models import AIConversation, AIConversationMessage
            from src.services.ai_service import generate_session_id
            
            # Get or create conversation session
            db = next(get_db())
            conversation = db.query(AIConversation).filter(
                AIConversation.user_id == current_user.id,
                AIConversation.is_active == True
            ).first()
            
            if not conversation:
                # Create new conversation session
                session_id = generate_session_id()
                conversation = AIConversation(
                    user_id=current_user.id,
                    session_id=session_id,
                    is_active=True
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            
            # Store user message
            user_message = AIConversationMessage(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                kanban_updates=None,
                tokens_used=len(request.message.split())
            )
            db.add(user_message)
            
            # Store AI response
            ai_message = AIConversationMessage(
                conversation_id=conversation.id,
                role="ai",
                content=response_text,
                kanban_updates=[update.model_dump() if hasattr(update, 'model_dump') else update for update in kanban_updates] if kanban_updates else None,
                tokens_used=len(response_text.split())
            )
            db.add(ai_message)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store conversation history: {e}")
            # Continue with response even if conversation storage fails
        
        # Apply Kanban updates if any (atomic operation)
        if kanban_updates:
            try:
                # Import services for database operations
                from src.services.board_service import BoardService
                from src.services.column_service import ColumnService
                from src.services.card_service import CardService
                from src.schemas.board import BoardUpdate
                from src.schemas.column import ColumnCreate, ColumnUpdate
                from src.schemas.card import CardCreate, CardUpdate
                
                # Get database session
                db = next(get_db())

                try:
                    # Apply each update in order
                    for update in kanban_updates:
                        logger.info(f"Applying update: {update.action} {update.element_type} id={update.element_id}")

                        if update.element_type == "card":
                            if update.action == ActionType.MOVE and update.element_id:
                                if update.target_column_id is not None:
                                    pos = update.new_position if update.new_position is not None else 999
                                    result = CardService.move_card(db, update.element_id, update.target_column_id, pos)
                                    if result:
                                        logger.info(f"Successfully moved card {update.element_id} to column {update.target_column_id}")
                                    else:
                                        logger.warning(f"Card {update.element_id} not found for move")
                            elif update.action == ActionType.CREATE:
                                card_data = CardCreate(**update.element_data)
                                CardService.create_card(db, card_data.column_id, card_data)
                            elif update.action == ActionType.UPDATE and update.element_id:
                                card_data = CardUpdate(**update.element_data)
                                CardService.update_card(db, update.element_id, card_data)
                            elif update.action == ActionType.DELETE and update.element_id:
                                CardService.delete_card(db, update.element_id)

                        elif update.element_type == "column":
                            if update.action == ActionType.CREATE:
                                column_data = ColumnCreate(**update.element_data)
                                ColumnService.create_column(db, column_data.board_id, column_data)
                            elif update.action == ActionType.UPDATE and update.element_id:
                                column_data = ColumnUpdate(**update.element_data)
                                ColumnService.update_column(db, update.element_id, column_data)
                            elif update.action == ActionType.DELETE and update.element_id:
                                ColumnService.delete_column(db, update.element_id)

                        elif update.element_type == "board":
                            if update.action == ActionType.CREATE:
                                board_data = BoardCreate(**update.element_data)
                                BoardService.create_board(db, current_user.id, board_data)
                            elif update.action == ActionType.UPDATE and update.element_id:
                                board_data = BoardUpdate(**update.element_data)
                                BoardService.update_board(db, update.element_id, board_data)
                            elif update.action == ActionType.DELETE and update.element_id:
                                BoardService.delete_board(db, update.element_id)

                    logger.info(f"Successfully applied {len(kanban_updates)} Kanban updates")

                except Exception as e:
                    db.rollback()
                    logger.error(f"Failed to apply Kanban updates: {e}")
                    response_text = f"AI analysis complete, but updates failed: {str(e)}"
                    explanation = "Some updates could not be applied due to errors"
                    kanban_updates = []
                    
            except Exception as e:
                logger.error(f"Error setting up transaction for Kanban updates: {e}")
                response_text = f"AI analysis complete, but could not prepare updates: {str(e)}"
                explanation = "Updates could not be prepared due to system error"
                kanban_updates = []
        
        # Final fallback for any remaining issues
        if not response_text or response_text.strip() == "":
            response_text = "I'm sorry, I encountered an unexpected error processing your request."
            explanation = "An unexpected error occurred"
        
        return AIKanbanResponse(
            user_response={
                "text": response_text,
                "explanation": explanation or "AI has analyzed your Kanban board and provided this response"
            },
            kanban_updates=kanban_updates,
            requires_confirmation=requires_confirmation
        )
        
    except Exception as e:
        logger.error(f"AI chat endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {str(e)}"
        )


@router.get("/health", response_model=AIHealthCheck)
async def ai_health_check(
    current_user=Depends(get_current_user)
) -> AIHealthCheck:
    """
    Health check endpoint for AI service.
    
    This endpoint checks if the AI service is properly configured
    and can connect to the OpenRouter API.
    """
    try:
        logger.info(f"User {current_user.username} checking AI health")
        
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