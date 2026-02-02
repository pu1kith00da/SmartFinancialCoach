# Smart Financial Coach - System Architecture (Phase 6 Complete)

## Database Schema & Relationships

```mermaid
erDiagram
    User ||--o{ Account : owns
    User ||--o{ Transaction : has
    User ||--o{ Category : creates
    User ||--o{ Budget : manages
    User ||--o{ Goal : sets
    User ||--o{ Subscription : subscribes
    User ||--o{ Bill : manages
    
    Account ||--o{ Transaction : contains
    Account {
        uuid id PK
        uuid user_id FK
        string name
        string account_type
        string provider
        decimal balance
        string currency
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Transaction ||--|| Category : categorized_as
    Transaction {
        uuid id PK
        uuid user_id FK
        uuid account_id FK
        uuid category_id FK
        decimal amount
        string description
        string transaction_type
        datetime transaction_date
        string status
        string merchant
        text notes
        datetime created_at
        datetime updated_at
    }
    
    Category {
        uuid id PK
        uuid user_id FK
        string name
        string category_type
        string color
        string icon
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Budget ||--|| Category : tracks
    Budget {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        decimal amount
        string period_type
        date start_date
        date end_date
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Goal {
        uuid id PK
        uuid user_id FK
        string name
        string goal_type
        decimal target_amount
        decimal current_amount
        date target_date
        string status
        text description
        datetime created_at
        datetime updated_at
    }
    
    Subscription {
        uuid id PK
        uuid user_id FK
        string name
        string description
        decimal amount
        string currency
        string billing_cycle
        date start_date
        date next_billing_date
        string status
        string detection_confidence
        decimal usage_limit
        decimal current_usage
        boolean has_trial
        date trial_end_date
        text notes
        datetime created_at
        datetime updated_at
    }
    
    Bill ||--o{ BillPayment : has_payments
    Bill {
        uuid id PK
        uuid user_id FK
        string name
        string description
        decimal amount
        boolean is_variable_amount
        decimal min_amount
        decimal max_amount
        string currency
        string frequency
        date due_date
        date next_due_date
        string status
        string category
        boolean auto_pay_enabled
        text notes
        datetime created_at
        datetime updated_at
    }
    
    BillPayment {
        uuid id PK
        uuid bill_id FK
        decimal amount_paid
        date payment_date
        string payment_method
        string status
        text notes
        datetime created_at
        datetime updated_at
    }
    
    User {
        uuid id PK
        string email
        string hashed_password
        string first_name
        string last_name
        string phone
        date date_of_birth
        string currency
        string timezone
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
    }
```

## API Architecture

```mermaid
graph TB
    Client[Frontend Client] --> API[FastAPI Server :8000]
    
    subgraph "API Layer"
        API --> Auth[Authentication JWT]
        API --> V1[/api/v1/]
        
        V1 --> Users[/users]
        V1 --> Accounts[/accounts]
        V1 --> Transactions[/transactions]
        V1 --> Categories[/categories]
        V1 --> Budgets[/budgets]
        V1 --> Goals[/goals]
        V1 --> Subscriptions[/subscriptions]
        V1 --> Bills[/bills]
    end
    
    subgraph "Service Layer"
        Users --> UserService[User Service]
        Accounts --> AccountService[Account Service]
        Transactions --> TransactionService[Transaction Service]
        Categories --> CategoryService[Category Service]
        Budgets --> BudgetService[Budget Service]
        Goals --> GoalService[Goal Service]
        Subscriptions --> SubscriptionService[Subscription Service]
        Bills --> BillService[Bill Service]
    end
    
    subgraph "Data Layer"
        UserService --> DB[(PostgreSQL Database)]
        AccountService --> DB
        TransactionService --> DB
        CategoryService --> DB
        BudgetService --> DB
        GoalService --> DB
        SubscriptionService --> DB
        BillService --> DB
    end
    
    subgraph "Authentication"
        Auth --> JWT[JWT Tokens]
        Auth --> Hash[Password Hashing]
    end
```

## Subscription & Bill Management Features

```mermaid
graph LR
    subgraph "Subscription Detection"
        Transactions --> Pattern[Pattern Recognition]
        Pattern --> Confidence[Confidence Scoring]
        Confidence --> Auto[Auto-Detection]
        Auto --> Manual[Manual Override]
    end
    
    subgraph "Bill Management"
        Bills --> Recurring[Recurring Bills]
        Bills --> Variable[Variable Amount Bills]
        Bills --> AutoPay[Auto-Pay Setup]
        Bills --> Reminders[Payment Reminders]
    end
    
    subgraph "Analytics"
        Auto --> Stats[Subscription Stats]
        Bills --> BillStats[Bill Analytics]
        Stats --> Calendar[Calendar View]
        BillStats --> Calendar
        Calendar --> Forecasting[Cost Forecasting]
    end
```

## Implementation Phases Status

```mermaid
gantt
    title Smart Financial Coach Development Progress
    dateFormat  YYYY-MM-DD
    section Phase 1-2: Foundation
    User Auth & Database Setup    :done, phase1, 2026-01-01, 2026-01-05
    
    section Phase 3-4: Core Features  
    Account Management           :done, phase3, 2026-01-05, 2026-01-10
    Transaction Processing       :done, phase4, 2026-01-10, 2026-01-15
    
    section Phase 5: Financial Planning
    Categories & Budgets         :done, phase5, 2026-01-15, 2026-01-25
    Goals Management            :done, phase5b, 2026-01-25, 2026-01-30
    
    section Phase 6: Subscriptions & Bills
    Subscription Detection       :done, phase6a, 2026-01-30, 2026-01-31
    Bill Management             :done, phase6b, 2026-01-30, 2026-01-31
    
    section Phase 7: Investment Tracking
    Investment Models           :active, phase7, 2026-01-31, 2026-02-07
    Portfolio Management        :phase7b, 2026-02-07, 2026-02-14
    
    section Phase 8: AI & Insights
    ML Models                   :phase8, 2026-02-14, 2026-02-21
    Predictive Analytics        :phase8b, 2026-02-21, 2026-02-28
```

## API Endpoints Summary

```mermaid
mindmap
  root((Smart Financial Coach API))
    Authentication
      POST /auth/register
      POST /auth/login
      POST /auth/refresh
    
    Users
      GET /users/me
      PUT /users/me
      DELETE /users/me
    
    Accounts
      GET /accounts
      POST /accounts
      GET /accounts/{id}
      PUT /accounts/{id}
      DELETE /accounts/{id}
    
    Transactions
      GET /transactions
      POST /transactions
      GET /transactions/{id}
      PUT /transactions/{id}
      DELETE /transactions/{id}
      POST /transactions/bulk-import
      GET /transactions/export
      GET /transactions/analytics
    
    Categories
      GET /categories
      POST /categories
      GET /categories/{id}
      PUT /categories/{id}
      DELETE /categories/{id}
    
    Budgets
      GET /budgets
      POST /budgets
      GET /budgets/{id}
      PUT /budgets/{id}
      DELETE /budgets/{id}
      GET /budgets/analytics
    
    Goals
      GET /goals
      POST /goals
      GET /goals/{id}
      PUT /goals/{id}
      DELETE /goals/{id}
      GET /goals/analytics
    
    Subscriptions
      GET /subscriptions
      POST /subscriptions
      GET /subscriptions/{id}
      PUT /subscriptions/{id}
      DELETE /subscriptions/{id}
      POST /subscriptions/detect
      GET /subscriptions/analytics
      GET /subscriptions/calendar
      POST /subscriptions/bulk-update
      PUT /subscriptions/{id}/cancel
      PUT /subscriptions/{id}/pause
      PUT /subscriptions/{id}/resume
      GET /subscriptions/upcoming
    
    Bills
      GET /bills
      POST /bills
      GET /bills/{id}
      PUT /bills/{id}
      DELETE /bills/{id}
      GET /bills/upcoming
      GET /bills/overdue
      POST /bills/{id}/payments
      GET /bills/{id}/payments
      PUT /bills/{id}/payments/{payment_id}
      DELETE /bills/{id}/payments/{payment_id}
      PUT /bills/{id}/autopay
      GET /bills/calendar
      GET /bills/analytics
      POST /bills/bulk-update
      GET /bills/{id}/history
      POST /bills/{id}/mark-paid
      PUT /bills/{id}/schedule
      GET /bills/payment-methods
      PUT /bills/{id}/remind
      GET /bills/categories
```

## Current System State (as of Phase 6 Completion)

### ✅ Completed Features
- **User Authentication**: JWT-based auth system
- **Account Management**: Bank account integration ready
- **Transaction Processing**: Full CRUD with analytics
- **Categories & Budgets**: Financial categorization and budget tracking
- **Goals Management**: Financial goal setting and tracking
- **Subscription Detection**: Automated recurring charge detection
- **Bill Management**: Comprehensive bill tracking and payment management

### 🚧 Database Migrations Applied
- `001_initial_schema.py` - Core user and account tables
- `002_add_transactions.py` - Transaction processing
- `003_add_categories.py` - Category management
- `004_add_budgets.py` - Budget tracking
- `005_add_goals.py` - Goal management
- `006_add_subscriptions_and_bills.py` - Subscription and bill tracking

### 📊 API Statistics
- **Total Endpoints**: 50+ endpoints across 8 resource types
- **Authentication**: JWT-based with refresh tokens
- **Validation**: Pydantic schemas for all requests/responses
- **Database**: AsyncSession with PostgreSQL
- **Documentation**: OpenAPI/Swagger auto-generated

### 🔄 Next Phase Ready
- **Phase 7**: Investment Tracking (Weeks 14-15)
  - Investment accounts and portfolios
  - Stock/bond/crypto tracking
  - Performance analytics
  - Diversification insights

## Technical Architecture Notes

### Database Design Principles
- UUID primary keys for security and distributed systems
- Soft deletes with `is_active` flags
- Audit trails with `created_at`/`updated_at`
- Proper foreign key relationships
- Enum types for constrained values

### API Design Patterns
- RESTful endpoints with standard HTTP methods
- Consistent error handling and status codes
- Pagination support for list endpoints
- Bulk operations for efficiency
- Analytics endpoints for insights

### Service Layer Architecture
- Separation of concerns between API and business logic
- Async/await patterns throughout
- Dependency injection for database sessions
- Modular service classes per domain

### Security Considerations
- JWT authentication with expiration
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for frontend integration

---

**Generated**: January 31, 2026 - Phase 6 Complete  
**Status**: All core financial management features implemented  
**Next**: Investment tracking and portfolio management (Phase 7)