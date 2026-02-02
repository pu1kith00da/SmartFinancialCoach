# Smart Financial Coach - Design Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technical Stack](#technical-stack)
4. [Design Decisions](#design-decisions)
5. [Data Models](#data-models)
6. [AI Integration](#ai-integration)
7. [Security Architecture](#security-architecture)
8. [API Design](#api-design)
9. [Frontend Architecture](#frontend-architecture)
10. [Future Enhancements](#future-enhancements)

---

## Executive Summary

Smart Financial Coach is an AI-powered personal financial management platform designed to help users take control of their finances through intelligent insights, automated tracking, and personalized coaching. The application provides:

- **Real-time financial visibility** through bank account integration
- **Personalized AI-powered insights** using Google Gemini 2.5 Pro
- **Actionable recommendations** for saving money and achieving financial goals

---

## System Architecture

The below figure presents the system architecture of the Smart Financial Coach before we go delve into detailed steps:
![System architecture of the Smart Financial Coach](SmartFinancialCoachArchitectureS.png)

### High-Level Architecture

The Smart Financial Coach follows a three-tier architecture pattern that separates concerns between presentation, business logic, and data management. The **Client Layer** consists of a Next.js 14 frontend running React 19 components that handle all user interactions through the dashboard, transaction views, goals management, and an AI-powered chatbot interface. The **API Layer** is powered by FastAPI with Python 3.11+, providing RESTful endpoints organized by resource type (authentication, Plaid integration, insights, chat, analytics). Within the API layer, the **Service Layer** encapsulates all business logic, including the AI/LLM client for Google Gemini integration, an MCP (Model Context Protocol) server for structured tool calling, and specialized services for transactions, budgets, goals, and insights. The **Data & External Services** layer includes PostgreSQL for persistent storage via async SQLAlchemy, Redis for caching and rate limiting, and external API integrations with Plaid for banking data and Google Gemini for AI capabilities. This layered architecture enables clear separation of concerns, independent scaling of components, and maintainable code organization.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Next.js 14 Frontend (React 19)                   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│  │  │  Dashboard  │ │Transactions │ │    Goals    │ │   Chatbot    │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ REST API (HTTPS)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend (Python 3.11+)                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │   Auth   │ │  Plaid   │ │ Insights │ │   Chat   │ │Analytics │  │   │
│  │  │  Router  │ │  Router  │ │  Router  │ │  Router  │ │  Router  │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         SERVICE LAYER                                │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│  │  │   AI/LLM    │ │Transaction  │ │   Budget    │ │     Goal     │  │   │
│  │  │   Client    │ │  Service    │ │   Service   │ │   Service    │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘  │   │
│  │                                                                      │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│  │  │    MCP      │ │  Insight    │ │Subscription │ │   Plaid      │  │   │
│  │  │   Server    │ │  Generator  │ │   Service   │ │   Service    │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA & EXTERNAL SERVICES                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│  │  PostgreSQL  │    │    Redis     │    │     External APIs            │  │
│  │   Database   │    │    Cache     │    │  ┌────────┐ ┌────────────┐  │  │
│  │  (asyncpg)   │    │              │    │  │ Plaid  │ │Google Gemini│  │  │
│  └──────────────┘    └──────────────┘    │  │  API   │ │    API     │  │  │
│                                          │  └────────┘ └────────────┘  │  │
│                                          └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

When a user performs an action in the application, the request flows through multiple layers with each component having a specific responsibility. The **React Component** captures user input and triggers state changes. **TanStack Query** (React Query) manages the request lifecycle, implementing caching strategies, deduplication, and optimistic updates to provide instant UI feedback. **Axios** handles the HTTP communication, adding authentication headers and formatting requests. The **FastAPI Router** receives the request, validates it against Pydantic schemas, and routes it to the appropriate endpoint. The **Service Layer** executes the business logic, coordinating between multiple data sources and services. **SQLAlchemy ORM** translates service-layer operations into SQL queries and manages the async database connection pool. Finally, data flows back through the layers, with TanStack Query caching the response for subsequent requests. For operations requiring external data, the service layer makes parallel calls to **External APIs** like Plaid for banking data or Google Gemini for AI-generated insights, aggregating results before returning to the client.

```
User Action → React Component → TanStack Query → Axios → FastAPI Router
                                                              ↓
                                                    Service Layer
                                                              ↓
                                            ┌─────────────────┴─────────────────┐
                                            ↓                                   ↓
                                     SQLAlchemy ORM                      External APIs
                                            ↓                           (Plaid, Gemini)
                                      PostgreSQL
```

---

## Technical Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.109.0 | High-performance async API framework |
| **Language** | Python | 3.11+ | Primary backend language |
| **ORM** | SQLAlchemy | 2.0.25 | Async database operations |
| **Database** | PostgreSQL | 15 | Primary data store |
| **DB Driver** | asyncpg | 0.29.0 | Async PostgreSQL driver |
| **Migrations** | Alembic | 1.13.1 | Database schema migrations |
| **Cache** | Redis | 7 | Session storage, rate limiting |
| **Validation** | Pydantic | 2.5.3 | Request/response validation |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Next.js | 16.1.6 | React framework with App Router |
| **UI Library** | React | 19.2.3 | Component-based UI |
| **Language** | TypeScript | 5.x | Type-safe JavaScript |
| **State Management** | TanStack Query | 5.90.20 | Server state management |
| **Local State** | Zustand | 5.0.10 | Client-side state |
| **HTTP Client** | Axios | 1.13.4 | API communication |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **Charts** | Recharts | 3.7.0 | Data visualization |
| **Icons** | Lucide React | 0.563.0 | Icon library |

### AI/ML Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Primary LLM** | Google Gemini | 2.5 Pro | Natural language understanding & generation |
| **Alternative LLMs** | OpenAI GPT-4o | Latest | Fallback AI provider |
| **Alternative LLMs** | Anthropic Claude | 3.5 | Fallback AI provider |
| **ML Library** | scikit-learn | 1.4.0 | Anomaly detection, pattern analysis |
| **Time Series** | Prophet | 1.1.5 | Spending forecasting |
| **Data Processing** | Pandas | 2.1.4 | Financial data analysis |

### External Services

| Service | Purpose |
|---------|---------|
| **Plaid API** | Bank account linking, transaction fetching |
| **Google Gemini API** | AI-powered insights and chatbot |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Development/deployment consistency |
| **Orchestration** | Docker Compose | Multi-service management |
| **Process Manager** | Uvicorn | ASGI server for FastAPI |

---

## Design Decisions

### 1. Async-First Architecture

**Decision:** Use async/await throughout the backend stack.

**Rationale:**
- Financial applications require handling multiple concurrent operations (bank syncs, AI processing)
- Async I/O dramatically improves throughput for I/O-bound operations
- SQLAlchemy 2.0's native async support enables efficient database operations

**Implementation:**
```python
# All database operations are async
async def get_transactions(user_id: UUID) -> List[Transaction]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Transaction).where(Transaction.user_id == user_id)
        )
        return result.scalars().all()
```

### 2. Model Context Protocol (MCP) for AI Tools

**Decision:** Implement MCP-style tool registry for AI chatbot instead of simple prompt engineering.

**Rationale:**
- Structured tool calling provides reliable, predictable AI responses
- Tools can access real user data through service layer
- Multi-step reasoning allows complex financial analysis
- Better separation of concerns between AI logic and data access

**Implementation:**
```python
class MCPServer:
    """MCP-style tool registry and execution engine."""
    
    def __init__(self, db: AsyncSession, user_id: UUID, llm_client):
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        return {
            "get_dashboard_summary": {...},
            "list_transactions": {...},
            "list_subscriptions": {...},
            "list_budgets": {...},
            "list_insights": {...},
            "list_goals": {...},
            "get_spending_analytics": {...},
        }
```

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `get_dashboard_summary` | Financial overview (income, spending, savings rate) |
| `list_transactions` | Query transactions with filters |
| `list_budgets` | Budget status and remaining amounts |
| `list_goals` | Financial goals and progress |
| `list_subscriptions` | Recurring charges analysis |
| `list_insights` | AI-generated savings recommendations |
| `get_spending_analytics` | Category-wise spending breakdown |

### 3. React Query for Server State

**Decision:** Use TanStack Query (React Query) instead of Redux for server state.

**Rationale:**
- Built-in caching, deduplication, and background refetching
- Optimistic updates for instant UI feedback
- Automatic cache invalidation patterns
- Reduces boilerplate compared to Redux + thunks/sagas

**Implementation:**
```typescript
// Mutation with optimistic updates
const deleteMutation = useMutation({
  mutationFn: (id: string) => api.goals.delete(id),
  onMutate: async (deletedId) => {
    await queryClient.cancelQueries({ queryKey: ["goals"] });
    const previousGoals = queryClient.getQueryData(["goals"]);
    queryClient.setQueryData(["goals"], (old) => ({
      ...old,
      goals: old.goals.filter((goal) => goal.id !== deletedId),
    }));
    return { previousGoals };
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["goals"] });
  },
});
```

### 4. Service Layer Pattern

**Decision:** Implement a clean service layer between API routes and database operations.

**Rationale:**
- Business logic is testable in isolation
- Services can be reused across different API endpoints
- AI tools can call the same services as HTTP endpoints
- Clear separation of concerns

**Service Structure:**
```
services/
├── ai_insight_generator.py  # AI-powered insight generation
├── analytics_service.py     # Dashboard & spending analytics
├── auth_service.py          # Authentication & authorization
├── budget_service.py        # Budget management
├── goal_service.py          # Financial goals
├── insight_service.py       # Insight CRUD operations
├── mcp_server.py            # AI tool registry
├── plaid_service.py         # Bank integration
├── subscription_service.py  # Recurring charges
└── transaction_service.py   # Transaction management
```

### 5. JWT with Refresh Tokens

**Decision:** Use JWT access tokens (30 min) with longer-lived refresh tokens (7 days).

**Rationale:**
- Short-lived access tokens minimize exposure window
- Refresh tokens enable seamless re-authentication
- Stateless authentication scales horizontally
- Token revocation via refresh token rotation

### 6. 50/30/20 Budget Rule

**Decision:** Implement the 50/30/20 budgeting rule as the default recommendation framework.

**Rationale:**
- Industry-standard, proven budgeting methodology
- Easy for users to understand
- Provides actionable spending limits
- Adaptable to different income levels

**Categories:**
- **50% Needs:** Bills, Groceries, Transportation
- **30% Wants:** Shopping, Food & Dining, Entertainment
- **20% Savings:** Goals, Emergency Fund

---

## Data Models

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    User     │       │   PlaidItem     │       │   PlaidAccount  │
├─────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)     │──────<│ user_id (FK)    │──────<│ item_id (FK)    │
│ email       │       │ access_token    │       │ account_id      │
│ password    │       │ institution_id  │       │ name            │
│ first_name  │       │ cursor          │       │ type            │
│ created_at  │       └─────────────────┘       │ balance         │
└─────────────┘                                 └─────────────────┘
       │
       │ 1:N
       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Transaction    │    │     Budget      │    │      Goal       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ user_id (FK)    │    │ user_id (FK)    │    │ user_id (FK)    │
│ amount          │    │ category        │    │ name            │
│ category        │    │ limit_amount    │    │ target_amount   │
│ merchant_name   │    │ spent_amount    │    │ current_amount  │
│ date            │    │ period          │    │ target_date     │
│ type            │    └─────────────────┘    │ status          │
└─────────────────┘                           └─────────────────┘
       │
       │ 1:N
       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Subscription   │    │     Insight     │    │  Conversation   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ user_id (FK)    │    │ user_id (FK)    │    │ user_id (FK)    │
│ name            │    │ type            │    │ title           │
│ amount          │    │ title           │    │ messages (JSON) │
│ frequency       │    │ message         │    │ created_at      │
│ status          │    │ priority        │    └─────────────────┘
│ detected_from   │    │ is_dismissed    │
└─────────────────┘    └─────────────────┘
```

### Key Models

**User Model:**
```python
class User(Base):
    __tablename__ = "users"
    
    id: UUID
    email: str (unique, indexed)
    hashed_password: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    mfa_secret: str (encrypted)
    created_at: datetime
    updated_at: datetime
```

**Transaction Model:**
```python
class Transaction(Base):
    __tablename__ = "transactions"
    
    id: UUID
    user_id: UUID (FK → users.id)
    plaid_transaction_id: str (nullable)
    amount: Decimal
    category: str
    merchant_name: str
    date: date
    type: TransactionType (INCOME/EXPENSE)
    is_recurring: bool
    created_at: datetime
```

**Insight Model:**
```python
class Insight(Base):
    __tablename__ = "insights"
    
    id: UUID
    user_id: UUID (FK → users.id)
    type: InsightType
    priority: InsightPriority
    title: str
    message: str
    category: str (nullable)
    amount: Decimal (nullable)
    context_data: JSON
    is_read: bool
    is_dismissed: bool
    created_at: datetime
```

---

## AI Integration

### Architecture Overview

The AI subsystem is designed with flexibility and reliability in mind, featuring a multi-provider LLM architecture and a structured tool-calling framework. The **LLM Client** acts as an abstraction layer that supports three AI providers: Google Gemini (primary), OpenAI (fallback), and Anthropic Claude (fallback), allowing the system to automatically switch providers if one is unavailable or to leverage different models for specific use cases. The **MCP Server (Model Context Protocol)** implements a tool registry pattern where each tool represents a specific financial operation (like fetching transactions or analyzing budgets) with well-defined schemas. When the AI needs data, it makes structured tool calls rather than relying on knowledge embedded in prompts, ensuring responses are grounded in the user's actual financial data. The tool execution engine calls the same service layer methods used by REST endpoints, maintaining consistency across the application. The **AI Insight Generator** is a separate component that proactively analyzes user data on a scheduled basis, detecting spending patterns using scikit-learn, identifying subscription duplicates, tracking goal progress, and generating personalized recommendations. This dual approach—reactive chatbot responses via MCP tools and proactive insight generation—provides users with both on-demand assistance and automated financial guidance.

```
┌────────────────────────────────────────────────────────────────┐
│                        AI SUBSYSTEM                             │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────┐   │
│  │   LLM Client    │    │      MCP Server (Tool Registry)  │   │
│  │                 │    │                                   │   │
│  │ ┌─────────────┐ │    │  ┌─────────────────────────────┐ │   │
│  │ │   Gemini    │ │◄───┤  │     Tool Definitions        │ │   │
│  │ │   (Primary) │ │    │  │  - get_dashboard_summary    │ │   │
│  │ └─────────────┘ │    │  │  - list_transactions        │ │   │
│  │                 │    │  │  - list_budgets             │ │   │
│  │ ┌─────────────┐ │    │  │  - list_goals               │ │   │
│  │ │   OpenAI    │ │    │  │  - list_subscriptions       │ │   │
│  │ │  (Fallback) │ │    │  │  - list_insights            │ │   │
│  │ └─────────────┘ │    │  │  - get_spending_analytics   │ │   │
│  │                 │    │  └─────────────────────────────┘ │   │
│  │ ┌─────────────┐ │    │                                   │   │
│  │ │  Anthropic  │ │    │  ┌─────────────────────────────┐ │   │
│  │ │  (Fallback) │ │    │  │     Tool Execution          │ │   │
│  │ └─────────────┘ │    │  │  Calls service layer        │ │   │
│  └─────────────────┘    │  │  Returns structured data    │ │   │
│                         │  └─────────────────────────────┘ │   │
│                         └─────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │               AI Insight Generator                        │  │
│  │  - Spending pattern analysis                              │  │
│  │  - Budget recommendations (50/30/20 rule)                 │  │
│  │  - Goal progress tracking                                 │  │
│  │  - Anomaly detection                                      │  │
│  │  - Subscription optimization                              │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Chatbot Flow

The chatbot interaction demonstrates the power of the Model Context Protocol approach to AI integration. When a user asks a question like "What subscriptions do I have?", the message is first combined with a comprehensive **System Prompt** (682 lines) that establishes the AI's persona as a knowledgeable financial advisor, provides explicit instructions on when and how to use each tool, and defines response formatting standards. This enriched context is sent to **Gemini 2.5 Pro API** which uses function calling capabilities to determine that the `list_subscriptions` tool is needed to answer the question. The AI generates a structured **Tool Call** with appropriate arguments (e.g., filtering for active subscriptions). The **MCP Server** receives this tool call and executes it by invoking the `subscription_service.get_all()` method from the service layer, which queries the database and returns actual user data. This real data is then fed back to Gemini, which synthesizes a natural language response that not only lists the subscriptions but can also provide intelligent analysis—like noticing duplicate services (Spotify and Apple Music) and suggesting cost-saving opportunities. This multi-step reasoning loop can iterate up to 5 times, allowing the AI to chain multiple tool calls to answer complex questions like "Am I on track with my financial goals and where can I save money?" by first fetching goals, then analyzing spending, then identifying savings opportunities.

```
User Message: "What subscriptions do I have?"
                    │
                    ▼
┌───────────────────────────────────────┐
│         System Prompt (682 lines)     │
│  - Financial advisor persona          │
│  - Tool usage instructions            │
│  - Response formatting rules          │
└───────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         Gemini 2.5 Pro API            │
│  Function calling with tools          │
└───────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│     Tool Call: list_subscriptions     │
│  Arguments: {"status": "active"}      │
└───────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│       MCP Server Tool Execution       │
│  → subscription_service.get_all()     │
│  → Returns: [{Netflix, Spotify, ...}] │
└───────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│      Gemini Generates Response        │
│  "You have 4 active subscriptions..." │
│  "Netflix: $15.99/month..."           │
│  "I noticed you have both Spotify     │
│   and Apple Music. Consider..."       │
└───────────────────────────────────────┘
```

### AI-Generated Insights

The system generates multiple types of insights:

| Insight Type | Trigger | Example |
|--------------|---------|---------|
| `spending_alert` | Category exceeds 80% of budget | "You've spent 88% of your dining budget" |
| `budget_alert` | Budget exceeded | "Entertainment budget exceeded by $35" |
| `savings_opportunity` | Duplicate services detected | "You have Spotify AND Apple Music" |
| `goal_progress` | Goal milestone reached | "You're 50% to your vacation goal!" |
| `goal_behind` | Goal off track | "Increase savings by $200/month to reach goal" |
| `anomaly` | Unusual transaction detected | "Unusually high $500 charge at Amazon" |

---

## Security Architecture

### Authentication Flow

The authentication system implements a secure token-based flow using JWT (JSON Web Tokens) with a two-token strategy for enhanced security and user experience. When a **User** submits login credentials, the system receives the **Login Request** containing email and password. The **Verify Password** step uses bcrypt to compare the submitted password against the stored hash, with a cost factor of 12 providing strong protection against brute-force attacks. Upon successful verification, the system **Issues Tokens**—specifically, an **Access Token** valid for 30 minutes and a **Refresh Token** valid for 7 days. The short-lived access token minimizes the window of vulnerability if compromised, containing only the user_id and expiration time. This token is included in the Authorization header of all subsequent API requests for authentication. The longer-lived refresh token enables seamless re-authentication without requiring the user to log in every 30 minutes; when the access token expires, the client automatically uses the refresh token to obtain a new access token pair without user intervention. Each refresh token includes a unique JTI (JWT ID) that enables token revocation—if suspicious activity is detected, specific refresh tokens can be invalidated, forcing re-authentication. This approach balances security (short access token lifespan) with usability (long refresh token enabling "remember me" functionality) while maintaining stateless authentication that scales horizontally.

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────┐
│  User   │────>│   Login     │────>│   Verify    │────>│  Issue   │
│         │     │  Request    │     │  Password   │     │  Tokens  │
└─────────┘     └─────────────┘     └─────────────┘     └──────────┘
                                                              │
    ┌─────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│  Tokens Issued:                                                   │
│  ┌─────────────────────────────┐  ┌────────────────────────────┐│
│  │      Access Token           │  │      Refresh Token          ││
│  │  - Valid: 30 minutes        │  │  - Valid: 7 days            ││
│  │  - Contains: user_id, exp   │  │  - Contains: user_id, jti   ││
│  │  - Usage: API authorization │  │  - Usage: Get new access    ││
│  └─────────────────────────────┘  └────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

### Security Measures

| Layer | Measure | Implementation |
|-------|---------|----------------|
| **Transport** | HTTPS Only | TLS 1.3 in production |
| **Authentication** | JWT Tokens | HS256 algorithm, short expiry |
| **Password** | bcrypt Hashing | Cost factor 12, 72-byte limit |
| **Sensitive Data** | Fernet Encryption | AES-128-CBC for tokens |
| **API** | Rate Limiting | Redis-backed, per-endpoint limits |
| **Headers** | Security Headers | HSTS, CSP, X-Frame-Options |
| **Input** | Pydantic Validation | Schema-based request validation |
| **MFA** | TOTP Support | pyotp with 30-second windows |

### Rate Limiting Configuration

```python
RATE_LIMITS = {
    "/api/v1/auth/login": (5, 60),        # 5 per minute
    "/api/v1/auth/register": (3, 60),     # 3 per minute
    "/api/v1/insights/generate": (10, 60), # 10 per minute
    "/api/v1/chat/message": (30, 60),     # 30 per minute
    "default": (100, 60)                   # 100 per minute
}
```

---

## API Design

### RESTful Endpoints

| Resource | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| **Auth** | POST | `/api/v1/auth/register` | User registration |
| | POST | `/api/v1/auth/login` | User login |
| | POST | `/api/v1/auth/refresh` | Refresh tokens |
| **Plaid** | POST | `/api/v1/plaid/link/token` | Create link token |
| | POST | `/api/v1/plaid/exchange` | Exchange public token |
| | GET | `/api/v1/plaid/accounts` | Get linked accounts |
| | POST | `/api/v1/plaid/sample-data` | Load demo data |
| **Transactions** | GET | `/api/v1/transactions` | List transactions |
| | GET | `/api/v1/transactions/{id}` | Get transaction |
| **Budgets** | GET | `/api/v1/budgets` | List budgets |
| | GET | `/api/v1/budgets/summary` | Budget summary |
| | PUT | `/api/v1/budgets/{id}` | Update budget |
| **Goals** | GET | `/api/v1/goals` | List goals |
| | POST | `/api/v1/goals` | Create goal |
| | DELETE | `/api/v1/goals/{id}` | Delete goal |
| **Insights** | GET | `/api/v1/insights` | List insights |
| | POST | `/api/v1/insights/generate` | Generate AI insights |
| **Chat** | POST | `/api/v1/chat/message` | Send chat message |
| | GET | `/api/v1/chat/conversations` | List conversations |
| **Analytics** | GET | `/api/v1/analytics/dashboard` | Dashboard summary |
| | GET | `/api/v1/analytics/spending` | Spending analytics |

### Response Format

```json
{
  "data": {
    "items": [...],
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-02-01T12:00:00Z"
  }
}
```

### Error Response

```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "status_code": 422
}
```

---

## Frontend Architecture

### Component Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Auth route group
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/           # Main dashboard
│   ├── transactions/        # Transaction history
│   ├── goals/               # Goal management
│   └── accounts/            # Linked accounts
├── components/
│   ├── ui/                  # Reusable UI primitives
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── progress.tsx
│   ├── dashboard/           # Dashboard components
│   │   ├── StatCard.tsx
│   │   ├── SpendingChart.tsx
│   │   └── BudgetProgress.tsx
│   └── chat/                # Chatbot components
│       └── Chatbot.tsx
├── lib/
│   ├── api.ts              # Axios instance & endpoints
│   └── utils.ts            # Utility functions
└── stores/
    └── authStore.ts        # Zustand auth state
```

### State Management Strategy

The frontend employs a strategic separation of state management responsibilities, using specialized tools for different types of state. **TanStack Query (React Query)** handles all server state—data that originates from and is synchronized with the backend API. This includes transactions, budgets, goals, and insights. TanStack Query provides sophisticated caching mechanisms that store fetched data in memory, automatically deduplicate simultaneous requests for the same data, implement background refetching to keep data fresh, and support optimistic updates where the UI reflects changes immediately while the server request happens asynchronously. For example, when deleting a goal, the goal disappears from the UI instantly (optimistic update), and if the server request fails, the UI automatically rolls back to the previous state. This approach eliminates the need for manual cache management and reduces backend load through intelligent request batching. **Zustand** manages client-side state—data that exists only in the browser and doesn't sync with the server. This includes authentication state (currently logged-in user, access tokens), UI state (modal visibility, sidebar open/closed), and user preferences. Zustand's state persists to localStorage, so authentication survives page refreshes without requiring re-login. This dual-tool strategy keeps server state concerns (caching, revalidation, synchronization) separate from client state concerns (UI interactions, local preferences), resulting in cleaner code and better performance than traditional monolithic state management solutions like Redux.

```
┌─────────────────────────────────────────────────────────────┐
│                    STATE MANAGEMENT                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              TanStack Query (Server State)              │ │
│  │  - Transactions, Budgets, Goals, Insights               │ │
│  │  - Automatic caching & background refetching            │ │
│  │  - Optimistic updates for mutations                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Zustand (Client State)                     │ │
│  │  - Authentication state (user, tokens)                  │ │
│  │  - UI state (modals, sidebar)                           │ │
│  │  - Persisted to localStorage                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Patterns

**Optimistic Updates:**
```typescript
const mutation = useMutation({
  mutationFn: deleteGoal,
  onMutate: async (id) => {
    await queryClient.cancelQueries({ queryKey: ["goals"] });
    const previous = queryClient.getQueryData(["goals"]);
    queryClient.setQueryData(["goals"], (old) => 
      old.filter(g => g.id !== id)
    );
    return { previous };
  },
  onError: (err, id, context) => {
    queryClient.setQueryData(["goals"], context.previous);
  },
});
```

---

## Future Enhancements

### Short-Term 

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| **Multi-Factor Authentication (MFA)** | TOTP-based 2FA using authenticator apps (Google Authenticator, Authy) | High |
| **OAuth Social Login** | Sign in with Google, GitHub, and Microsoft accounts | High |
| **Real-time Notifications** | WebSocket-based alerts for budget thresholds | High |
| **Bill Reminders** | Automated reminders for upcoming bills | High |
| **Export to CSV/PDF** | Download transaction history and reports | Medium |
| **Dark Mode** | Theme toggle for user preference | Medium |
| **Mobile PWA** | Progressive Web App for mobile access | Medium |

### Medium-Term 

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| **Spending Forecasts** | ML-based spending predictions using Prophet | High |
| **Smart Categorization** | AI-powered automatic transaction categorization | High |
| **Biometric Authentication** | Face ID, Touch ID, and fingerprint login for mobile | Medium |
| **Session Management** | View and revoke active sessions across devices | Medium |
| **Investment Tracking** | Portfolio integration via Plaid investments | Medium |
| **Security Audit Logs** | Detailed logging of all security-related events | Medium |
| **Family Accounts** | Shared household financial management | Low |

### Long-Term 

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| **Hardware Security Keys** | FIDO2/WebAuthn support for physical security keys (YubiKey) | High |
| **End-to-End Encryption** | Client-side encryption for sensitive financial data | High |
| **Voice Interface** | Voice commands for hands-free financial queries | Medium |
| **Credit Score Monitoring** | Integration with credit bureaus | Medium |
| **Tax Optimization** | AI suggestions for tax-deductible expenses | Medium |
| **Financial Planning** | Long-term retirement & education planning | Low |
| **Community Features** | Anonymous spending comparisons | Low |

### Technical Debt & Improvements

| Area | Improvement | Effort |
|------|-------------|--------|
| **Testing** | Increase test coverage to 80%+ | Medium |
| **Monitoring** | Add OpenTelemetry distributed tracing | Medium |
| **CI/CD** | GitHub Actions pipeline with staging env | Low |
| **Documentation** | OpenAPI spec auto-generation | Low |
| **Performance** | Redis caching for dashboard queries | Medium |
| **Security** | SOC 2 compliance preparation | High |
| **Security** | Penetration testing and vulnerability scanning | High |
| **Security** | Implement rate limiting per user (not just per IP) | Medium |
| **Security** | Add CAPTCHA for registration and sensitive operations | Medium |

---

## Conclusion

Smart Financial Coach demonstrates a modern, scalable architecture that combines:

1. **Async Python backend** for high-performance financial operations
2. **React 19 with TanStack Query** for responsive, cache-efficient frontend
3. **Google Gemini AI** with MCP tools for intelligent financial coaching
4. **Plaid integration** for secure bank connectivity
5. **Defense-in-depth security** with JWT, encryption, and rate limiting

The modular design enables rapid feature development while maintaining code quality and security standards required for financial applications.

---
