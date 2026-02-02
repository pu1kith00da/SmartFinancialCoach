"""
Schemas for chat API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID for context")


class ChatResponse(BaseModel):
    """Response from chat API."""
    response: str = Field(..., description="Assistant's response (may be multiline)")
    conversation_id: UUID = Field(..., description="Conversation ID")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured data from tools")


class ToolCall(BaseModel):
    """Represents a tool call from the LLM."""
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    """Result from executing a tool."""
    name: str
    result: Any
    error: Optional[str] = None
