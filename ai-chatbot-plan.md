# AI Chatbot Implementation Plan

## Overview
Add an AI-powered chatbot to the Smart Fin Coach dashboard that can answer user questions about their finances by intelligently using the existing backend APIs through an MCP (Model Context Protocol) server architecture.

## Architecture

### High-Level Design
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌──────────────┐                    ┌──────────────┐       │
│  │  Dashboard   │                    │   Chatbot    │       │
│  │   Pages      │                    │   Interface  │       │
│  └──────────────┘                    └──────┬───────┘       │
│                                              │               │
└──────────────────────────────────────────────┼───────────────┘
                                               │
                                               ▼
                          ┌────────────────────────────────┐
                          │   Chatbot API Gateway          │
                          │   (/api/v1/chat)               │
                          └────────────┬───────────────────┘
                                       │
                          ┌────────────▼───────────────────┐
                          │   MCP Server                   │
                          │  (Model Context Protocol)      │
                          │                                │
                          │  • Tool Registry               │
                          │  • LLM Integration (Gemini)    │
                          │  • Context Management          │
                          └────────────┬───────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
            │  Tool: Get    │  │  Tool: Get   │  │  Tool: Get   │
            │  Transactions │  │  Analytics   │  │  Insights    │
            └───────┬───────┘  └──────┬───────┘  └──────┬───────┘
                    │                 │                  │
                    └─────────────────┼──────────────────┘
                                      ▼
                          ┌────────────────────────────┐
                          │   Existing FastAPI Backend │
                          │   (All Current Endpoints)  │
                          └────────────────────────────┘
```

## Components

### 1. MCP Server (`/backend/app/services/mcp_server.py`)

**Purpose**: Central hub that registers tools, manages LLM interactions, and orchestrates API calls.

**Key Features**:
- Tool registration system (each API endpoint becomes a tool)
- Schema validation for tool inputs
- Context management (conversation history)
- Multi-step reasoning (chain multiple API calls)
- Response formatting (non-streaming MVP)

#### MCP “Server” Deployment Options
This plan uses an MCP-style tool registry and execution loop. You can deploy it in two ways:

1) **In-process (recommended for MVP)**: Implement `MCPServer` as a normal Python service class inside the FastAPI backend. Tools call internal service-layer methods (e.g., `AnalyticsService`, `TransactionService`) using the same `AsyncSession` as the request.

2) **Standalone MCP server (future)**: Run a separate MCP process (stdio/JSON-RPC) that exposes the same tools. The backend/chat route would forward tool calls to that MCP process.

For this MVP, use option (1) to minimize latency and avoid “calling our own HTTP APIs” from inside the backend.

**Tool Registry**:
```python
TOOLS = {
    "get_dashboard_summary": {
        "description": "Get the same financial overview used by the dashboard (income, spending, savings rate, budgets, goals, etc.)",
        "endpoint": "/api/v1/analytics/dashboard",
        "method": "GET",
        "parameters": {}
    },
    "list_transactions": {
        "description": "Retrieve transactions with filters (category, date range, search term, pagination)",
        "endpoint": "/api/v1/transactions",
        "method": "GET",
        "parameters": {
            "limit": "int (optional)",
            "offset": "int (optional)",
            "start_date": "str (optional) - YYYY-MM-DD",
            "end_date": "str (optional) - YYYY-MM-DD",
            "category": "str (optional)",
            "search": "str (optional) - matches name/merchant"
        }
    },
    "get_spending_analytics": {
        "description": "Get spending analytics for a period (includes totals and by-category breakdown)",
        "endpoint": "/api/v1/analytics/spending",
        "method": "GET",
        "parameters": {
            "start_date": "str (optional) - YYYY-MM-DD",
            "end_date": "str (optional) - YYYY-MM-DD",
            "compare": "bool (optional) - compare with previous period"
        }
    },
    "list_insights": {
        "description": "List AI-generated insights (supports filtering by type, priority, read/dismissed)",
        "endpoint": "/api/v1/insights",
        "method": "GET",
        "parameters": {
            "type": "str (optional)",
            "priority": "str (optional)",
            "is_read": "bool (optional)",
            "is_dismissed": "bool (optional)",
            "category": "str (optional)",
            "limit": "int (optional)",
            "offset": "int (optional)"
        }
    },
    "list_goals": {
        "description": "List financial goals and progress",
        "endpoint": "/api/v1/goals",
        "method": "GET",
        "parameters": {
            "status": "str (optional)",
            "goal_type": "str (optional)",
            "skip": "int (optional)",
            "limit": "int (optional)"
        }
    },
    "get_spending_trends": {
        "description": "Get multi-month spending trends",
        "endpoint": "/api/v1/analytics/trends/spending",
        "method": "GET",
        "parameters": {
            "months": "int (optional) - 1..24"
        }
    }
}
```

#### Repo Alignment Notes (Current Codebase)
- The backend trends route is `GET /api/v1/analytics/trends/spending`.
- If the dashboard (or this chatbot) needs trends, ensure the frontend client points to `/api/v1/analytics/trends/spending` (not `/api/v1/analytics/trends`).
- The chatbot tools should mirror the same endpoints the dashboard uses to keep answers consistent with what users see.

### 2. Chat API Endpoint (`/backend/app/api/v1/chat.py`)

**New Endpoint**: `POST /api/v1/chat/message`

**Request**:
```json
{
  "message": "How much did I spend on dining last month?",
    "conversation_id": "uuid (optional)"
}
```

**Response**:
```json
{
  "response": "You spent $523.45 on Food & Dining last month. This was across 34 transactions, with your highest spending at Chipotle ($127.50, 12 visits).",
  "conversation_id": "uuid",
    "tools_used": ["list_transactions", "get_spending_analytics"],
  "data": {
    "category_total": 523.45,
    "transaction_count": 34,
    "top_merchant": "Chipotle",
    "top_merchant_amount": 127.50
  }
}
```

**Response Formatting Note**:
- The `response` string may be **multiline** (contain `\n`) to support readable formatting (e.g., bullet lists, short paragraphs). MVP can treat it as plain text; later you can optionally render Markdown.

### 3. Frontend Chatbot Component (`/frontend/components/chat/`)

**Files**:
- `Chatbot.tsx` - Main chat interface
- `ChatMessage.tsx` - Individual message component
- `ChatInput.tsx` - Input field with suggestions
- `ChatSuggestions.tsx` - Quick action buttons

**Features**:
- Floating chat button on dashboard
- Expandable chat panel
- Message history in browser
- Typing indicators
- Suggested questions
- Data visualization in responses (charts, tables)
- Voice input support

## Implementation Steps

### Phase 1: Backend Foundation (Week 1)

#### Step 1.1: MCP Server Core
```python
# /backend/app/services/mcp_server.py

class MCPServer:
    def __init__(self, llm_client, user_context):
        self.llm_client = llm_client
        self.user_context = user_context  # User ID, auth token
        self.tools = self._register_tools()
        self.conversation_history = []
    
    def _register_tools(self) -> Dict[str, Tool]:
        """Register all available tools from API endpoints"""
        # Convert API endpoints to LLM tool schemas
        
    async def process_message(self, message: str) -> ChatResponse:
        """Main entry point - process user message"""
        # 1. Add message to conversation history
        # 2. Send to LLM with tool schemas
        # 3. Execute requested tools
        # 4. Format and return response
        
    async def execute_tool(self, tool_name: str, parameters: Dict) -> Any:
        """Execute a registered tool by calling backend API"""
        # MVP: Call service-layer methods directly using `AsyncSession` and `current_user`
        # (avoid HTTP calls to our own API from inside the backend)
        
    def format_response(self, llm_response: str, tool_results: List) -> str:
        """Format final response with data from tools"""
```

#### Step 1.2: Chat API Endpoint
```python
# /backend/app/api/v1/chat.py

@router.post("/message")
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process chat message and return AI response"""
    mcp = MCPServer(
        llm_client=get_llm_client(),
        user_context={"user_id": current_user.id, "db": db}
    )
    
    response = await mcp.process_message(request.message)
    
    # Save conversation to database
    await save_conversation(db, current_user.id, request, response)
    
    return response
```

#### Step 1.3: Conversation Storage
```python
# /backend/app/models/conversation.py

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    title = Column(String)  # Auto-generated from first message
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True)
    conversation_id = Column(UUID, ForeignKey("conversations.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    tools_used = Column(JSON)  # List of tools called
    tool_results = Column(JSON)  # Data from API calls
    created_at = Column(DateTime)
```

### Phase 2: Frontend Integration (Week 2)

#### Step 2.1: Chat UI Component
```typescript
// /frontend/components/chat/Chatbot.tsx

export function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (text: string) => {
    setIsLoading(true);
    
    // Add user message
    const userMsg = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    
    // Call API
    const response = await api.chat.sendMessage({ message: text });
    
    // Add assistant response
    const assistantMsg = {
      role: "assistant",
      content: response.response,
      data: response.data
    };
    setMessages(prev => [...prev, assistantMsg]);
    
    setIsLoading(false);
  };

  return (
    <>
      {/* Floating chat button */}
      <button onClick={() => setIsOpen(true)}>
        💬 Ask AI
      </button>
      
      {/* Chat panel */}
      {isOpen && (
        <div className="chat-panel">
          <ChatHeader onClose={() => setIsOpen(false)} />
          <ChatMessages messages={messages} />
          <ChatSuggestions onSelect={sendMessage} />
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      )}
    </>
  );
}
```

#### Step 2.2: Suggested Questions
```typescript
const SUGGESTED_QUESTIONS = [
  "How much did I spend this month?",
  "What are my top spending categories?",
  "Show my recent transactions",
  "How am I doing on my savings goal?",
  "Where can I save money?",
  "Compare my spending to last month",
  "What's my biggest expense this month?",
  "Am I on track with my budget?"
];
```

#### Step 2.3: Response Formatting
```typescript
// /frontend/components/chat/ChatMessage.tsx

function ChatMessage({ message }) {
  // Render based on response type
  if (message.data?.chart) {
    return <ChartResponse data={message.data} />;
  }
  
  if (message.data?.transactions) {
    return <TransactionList items={message.data.transactions} />;
  }
  
  return <TextResponse content={message.content} />;
}
```

### Phase 3: LLM Tool Integration (Week 3)

#### Step 3.1: Tool Schema for Gemini
```python
# Format tools for Gemini Function Calling API

def get_tool_schemas() -> List[Dict]:
    return [
        {
            "name": "get_transactions",
            "description": "Retrieve user's transactions with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions to return"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (e.g., 'Food & Dining')"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    }
                }
            }
        },
        # ... other tools
    ]
```

#### Step 3.2: Multi-Step Reasoning
```python
async def process_complex_query(self, message: str):
    """Handle queries requiring multiple API calls"""
    
    # Example: "Compare my dining spending to last month"
    # Step 1: Get current month dining spending
    # Step 2: Get last month dining spending
    # Step 3: Calculate difference and format response
    
    conversation = [
        {"role": "user", "content": message}
    ]
    
    max_iterations = 5
    for i in range(max_iterations):
        response = await self.llm_client.chat_with_tools(
            messages=conversation,
            tools=get_tool_schemas()
        )
        
        # Check if LLM wants to use a tool
        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = await self.execute_tool(
                    tool_call.name,
                    tool_call.arguments
                )
                
                # Add tool result to conversation
                conversation.append({
                    "role": "function",
                    "name": tool_call.name,
                    "content": json.dumps(result)
                })
        else:
            # LLM has final answer
            return response.content
```

## Example Interactions

### Example 1: Simple Query
**User**: "How much did I spend on groceries this month?"

**Process**:
1. LLM calls `get_transactions(category="Groceries", start_date="2026-01-01")`
2. Backend returns transactions
3. LLM formats response

**Response**: "You spent $450.23 on groceries this month across 8 transactions. Your most frequent store was Safeway ($245.10, 5 visits)."

### Example 2: Complex Multi-Step Query
**User**: "Am I spending more on dining out compared to last month?"

**Process**:
1. LLM calls `get_spending_analytics(start_date="2026-01-01", end_date="2026-01-31")`
2. Reads January Food & Dining from the returned `by_category`
3. LLM calls `get_spending_analytics(start_date="2025-12-01", end_date="2025-12-31")`
4. Reads December Food & Dining from the returned `by_category`
5. LLM calculates difference and percentage

**Response**: "Yes, you spent $523.45 on Food & Dining in January, which is $36.25 (7.4%) more than December's $487.20. Your most frequent spot was Chipotle with 12 visits ($127.50)."

### Example 3: Goal Tracking
**User**: "How am I doing on my vacation savings goal?"

**Process**:
1. LLM calls `get_goals()`
2. Finds vacation goal
3. Calculates progress

**Response**: "Your vacation fund is at $2,450 out of $5,000 target (49%). You're 2 months into your 6-month goal timeline, so you're slightly ahead of schedule. At your current rate, you'll reach your goal by March 15th."

### Example 4: Insights & Recommendations
**User**: "Where can I save money this month?"

**Process**:
1. LLM calls `get_insights(type="savings_opportunity")`
2. Gets AI-generated recommendations
3. Formats top 3

**Response**: "Here are 3 ways to save:

1. **Reduce Chipotle visits** - You spent $127.50 (12 visits). Reducing to 8 visits saves $42/month.
2. **Optimize Shell fuel costs** - $236.80 at Shell. Using fuel rewards could save $15/month.
3. **Consolidate Amazon orders** - 34 orders ($1,463). Prime card gives 5% back = $73 savings."

## Technical Specifications

### LLM Configuration
- **Model**: gemini-1.5-pro or gemini-2.0-flash-thinking-exp
- **Temperature**: 0.3 (factual, data-driven responses)
- **Max Response Tokens**: 4096
- **Function Calling**: Enabled
- **System Prompt**: "You are a helpful financial assistant..."

### API Rate Limiting
- 10 messages per minute per user
- 100 messages per day per user
- Implement conversation throttling

### Caching Strategy
- Cache tool results for 5 minutes
- Cache similar queries with same parameters
- Invalidate on new transactions/updates

### Security
- All API calls use user's authentication token
- Row-level security (user can only access own data)
- Sanitize LLM inputs/outputs
- Rate limiting per user

## Database Schema

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tools_used JSONB,
    tool_results JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

## File Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   └── chat.py                    # NEW - Chat endpoints
│   ├── models/
│   │   ├── conversation.py            # NEW - Conversation model
│   │   └── message.py                 # NEW - Message model
│   ├── schemas/
│   │   └── chat.py                    # NEW - Chat request/response schemas
│   └── services/
│       ├── mcp_server.py              # NEW - MCP server implementation
│       └── chat_service.py            # NEW - Chat business logic
│
frontend/
├── components/
│   └── chat/
│       ├── Chatbot.tsx                # NEW - Main chat interface
│       ├── ChatMessage.tsx            # NEW - Message display
│       ├── ChatInput.tsx              # NEW - Input field
│       ├── ChatSuggestions.tsx        # NEW - Quick actions
│       └── ChatHeader.tsx             # NEW - Chat header
├── hooks/
│   └── useChat.ts                     # NEW - Chat state management
└── lib/
    └── api.ts                         # UPDATE - Add chat endpoints
```

## Testing Strategy

### Unit Tests
- Test tool registration
- Test tool execution
- Test response formatting
- Test conversation storage

### Integration Tests
- Test multi-step queries
- Test error handling
- Test API authentication
- Test rate limiting

### E2E Tests
- Test complete user flows
- Test UI interactions
- Test long-running queries (multi-tool chains)

## Future Enhancements

1. **Voice Input/Output**
   - Speech-to-text for queries
   - Text-to-speech for responses

2. **Proactive Insights**
   - Chatbot suggests questions based on recent activity
   - Weekly financial check-in prompts

3. **Multi-Modal Responses**
   - Charts and graphs in chat
   - Transaction visualizations
   - Budget progress bars

4. **Conversation Memory**
   - Reference previous conversations
   - Learn user preferences
   - Personalized suggestions

5. **Action Capabilities**
   - "Set a budget for dining"
   - "Create a savings goal"
   - "Mark this transaction as recurring"

## Success Metrics

- **Engagement**: % of users who try chatbot
- **Retention**: Average messages per session
- **Utility**: % of queries successfully answered
- **Speed**: Average response time < 2 seconds
- **Accuracy**: User satisfaction ratings

## Timeline

- **Week 1**: Backend MCP server + Chat API
- **Week 2**: Frontend chatbot UI + Integration
- **Week 3**: LLM tool integration + Multi-step reasoning
- **Week 4**: Testing, polish, deployment

## Conclusion

This AI chatbot will transform the Smart Fin Coach dashboard from a passive data display into an interactive financial advisor that users can ask questions and get personalized insights on demand.
