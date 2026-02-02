"""
Chat API endpoints for AI chatbot.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.mcp_server import MCPServer
from app.core.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process chat message and return AI response.
    
    The chatbot uses MCP-style tool calling to answer questions by
    accessing the user's financial data through service-layer methods.
    """
    try:
        # Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = uuid4()
            conversation = Conversation(
                id=conversation_id,
                user_id=current_user.id,
                title=request.message[:100]  # Use first message as title
            )
            db.add(conversation)
        
        # Create MCP server instance
        llm_client = get_llm_client()
        mcp = MCPServer(
            db=db,
            user_id=current_user.id,
            llm_client=llm_client
        )
        
        # Process message
        logger.info(f"Processing message: {request.message[:100]}")
        result = await mcp.process_message(request.message)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"],
            tools_used=result.get("tools_used", []),
            tool_results=result.get("data")
        )
        db.add(assistant_message)
        
        await db.commit()
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            tools_used=result.get("tools_used", []),
            data=result.get("data")
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/conversations")
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's chat conversations."""
    from sqlalchemy import select
    from app.models.conversation import Conversation
    
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    conversations = result.scalars().all()
    
    return {
        "conversations": [
            {
                "id": str(c.id),
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in conversations
        ]
    }
