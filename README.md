# Smart Financial Coach

An AI-powered personal financial management platform that helps you take control of your finances with intelligent insights, budget tracking, goal management, and personalized financial coaching powered by Google Gemini AI.

Design Document: [DESIGN_DOCUMENTATION.md](https://github.com/pu1kith00da/SmartFinancialCoach/blob/main/DESIGN_DOCUMENTATION.md)

Demo Link: https://youtu.be/eqmDgPwv76U

![Diagram of Smart Financial Coach Application](SmartFinancialCoachAppS.png)

## Features

Smart Financial Coach provides comprehensive financial management capabilities designed to give users complete visibility into their finances while leveraging artificial intelligence for personalized recommendations. The platform integrates with banks through Plaid's secure API, automatically categorizes transactions, and uses Google Gemini AI to analyze spending patterns and generate actionable insights. Users can track progress toward financial goals, monitor subscription services, and receive real-time alerts when budgets are exceeded, all through an intuitive dashboard interface.

###  Financial Management
- **Bank Account Integration**: Connect your bank accounts securely via Plaid
- **Transaction Tracking**: Automatic transaction categorization and monitoring
- **Budget Management**: Set and track budgets across 7 main categories (Groceries, Shopping, Food & Dining, Bills, Transportation, Other, Savings)
- **Goal Setting**: Create and track financial goals with progress monitoring
- **Subscription Tracking**: Identify and manage recurring subscriptions

###  AI-Powered Insights
- **Intelligent Chatbot**: Ask questions about your finances in natural language
- **Savings Recommendations**: Get personalized tips on where you can save money
- **Spending Analysis**: AI-generated insights based on your transaction patterns
- **Budget Recommendations**: Smart suggestions using the 50/30/20 rule
- **Trend Detection**: Identify spending patterns and anomalies

###  Analytics & Visualization
- **Dashboard Overview**: View net worth, monthly income/expenses, and savings rate
- **Spending Charts**: Visual breakdown of spending by category
- **Transaction History**: Detailed transaction lists with filtering
- **Budget Progress**: Visual indicators showing budget utilization
- **Goal Progress**: Track your progress toward financial goals

###  Security & Privacy
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Password Hashing**: bcrypt encryption for user passwords
- **Field-Level Encryption**: Sensitive data encrypted at rest
- **MFA Support**: Two-factor authentication with TOTP
- **Secure Banking**: Plaid-powered bank connections with bank-level security

##  Quick Start

Getting started with Smart Financial Coach requires setting up both the backend Python server and the frontend Next.js application, along with PostgreSQL and Redis services running in Docker. The setup process involves installing dependencies, configuring API keys for Plaid and Google Gemini, and running database migrations. Once configured, the entire application stack runs locally on your machine, with the frontend accessible at localhost:3000 and the backend API at localhost:8000.

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/downloads)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd smart-fin-coach
   ```

2. **Set up environment variables**
   
   Create a `.env` file in the `backend` directory:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` and configure the following:
   
   Edit `backend/.env` and configure the following:
   
   ```bash
   # Application Settings
   APP_NAME=Smart Financial Coach
   DEBUG=true
   ENVIRONMENT=development
   
   # Security (REQUIRED - Generate secure keys)
   SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
   ENCRYPTION_KEY=your-encryption-key-here  # Generate with: openssl rand -base64 32
   
   # Database (Uses Docker - no changes needed)
   DATABASE_URL=postgresql+asyncpg://fincoach:fincoach_dev_password@localhost:5432/fincoach
   
   # Redis (Uses Docker - no changes needed)
   REDIS_URL=redis://localhost:6379
   
   # Plaid API (REQUIRED - Get from https://dashboard.plaid.com/)
   PLAID_CLIENT_ID=your-plaid-client-id
   PLAID_SECRET=your-plaid-secret
   PLAID_ENV=sandbox  # Use 'sandbox' for testing
   
   # Google Gemini AI (REQUIRED - Get from https://aistudio.google.com/apikey)
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-2.0-flash-exp  # Or gemini-1.5-pro, gemini-1.5-flash
   
   # JWT Token Settings
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # CORS Settings
   CORS_ORIGINS=["http://localhost:3000"]
   ```
   
   **Important API Keys:**
   - **SECRET_KEY**: Generate with `openssl rand -hex 32` in terminal
   - **ENCRYPTION_KEY**: Generate with `openssl rand -base64 32` in terminal
   - **PLAID_CLIENT_ID & PLAID_SECRET**: Sign up at [Plaid](https://dashboard.plaid.com/signup) and create a sandbox app
   - **GEMINI_API_KEY**: Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey)

3. **Start Docker services (PostgreSQL & Redis)**
   ```bash
   docker-compose up -d postgres redis
   ```
   
   Verify services are running:
   ```bash
   docker ps
   ```
   You should see containers named `smart-fin-coach-postgres-1` and `smart-fin-coach-redis-1`.

### Backend Server Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create Python virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   
   The backend should now be running at:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Frontend Server Setup

1. **Open a new terminal** (keep the backend running in the first terminal)

2. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Start the frontend development server**
   ```bash
   npm run dev
   ```
   
   The frontend should now be running at:
   - Application: http://localhost:3000

5. **Access the application**
   
   Open your browser and go to http://localhost:3000
   
   You can now:
   - Register a new account
   - Connect your bank account (use Plaid sandbox credentials)
   - View transactions, set budgets, create goals
   - Chat with the AI financial coach

##  Stopping the Application

### Terminate Frontend Server
In the terminal running the frontend:
```bash
# Press Ctrl+C to stop the server
```

Or kill the process:
```bash
lsof -ti:3000 | xargs kill -9
```

### Terminate Backend Server
In the terminal running the backend:
```bash
# Press Ctrl+C to stop the server
```

Or kill the process:
```bash
lsof -ti:8000 | xargs kill -9
```

### Stop Docker Services
```bash
docker-compose down
```

To stop and remove all data (database will be cleared):
```bash
docker-compose down -v
```

## 🔄 Restarting the Application

After initial setup, you can quickly restart the application with the following steps:

1. **Start Docker services**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Start backend** (in one terminal)
   ```bash
   cd backend
   source venv/bin/activate  # On macOS/Linux
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Start frontend** (in another terminal)
   ```bash
   cd frontend
   npm run dev
   ```

## Testing with Plaid Sandbox

Plaid's sandbox environment allows you to test bank integration features without connecting real financial accounts. The sandbox provides simulated bank institutions with test credentials that mimic the real authentication flow, including multi-factor authentication prompts. You can generate sample transaction data spanning multiple months across different categories, enabling comprehensive testing of budgeting, spending analysis, and AI insight generation features without risking actual financial data.

When using Plaid in sandbox mode, you can test with dummy credentials:

### Connecting a Bank Account
1. Click "Connect Bank Account" in the dashboard
2. Select any bank from the list
3. Use these credentials:
   - **Username**: `user_good`
   - **Password**: `pass_good`
   - **MFA**: `1234` (if prompted)

### Available Test Banks
- **Chase**: Standard checking/savings accounts
- **Bank of America**: Credit cards and checking
- **Wells Fargo**: Multiple account types
- **Citi**: Investment and checking accounts

### Populating Sandbox Transactions
After connecting an account, click "Populate Sandbox Transactions" on the dashboard to generate test transaction data.

## Using the AI Chatbot

The AI-powered chatbot leverages Google Gemini's advanced language understanding to provide conversational financial advice based on your actual transaction data. Using the Model Context Protocol approach, the chatbot can access specialized tools to query your transactions, budgets, goals, and subscriptions in real-time, ensuring responses are grounded in your current financial situation. The AI can perform multi-step reasoning, chaining together multiple data queries to answer complex questions like identifying savings opportunities or analyzing spending trends across categories.

The AI chatbot can answer questions about your finances. Try asking:

**Budget Questions:**
- "What are my budgets?"
- "How am I doing with my budget?"
- "Am I over budget in any category?"
- "Show me my spending by category"

**Savings & Recommendations:**
- "How can I save money?"
- "Where can I cut spending?"
- "Evaluate my transactions and tell me how to save"
- "Give me savings tips"

**Transactions & Spending:**
- "Show me my recent transactions"
- "What did I spend on groceries?"
- "What are my top spending categories?"

**Goals & Analytics:**
- "Show me my financial goals"
- "What's my spending trend?"
- "How is my net worth?"

## Project Structure

The application follows a clean separation of concerns with distinct backend and frontend codebases. The backend implements a service-layer architecture where API routes delegate business logic to service classes, which in turn interact with SQLAlchemy models for database operations. The frontend uses Next.js 14's App Router for file-based routing, with components organized by feature and a centralized API client for all backend communication. Database migrations are managed through Alembic, allowing version-controlled schema changes that can be applied incrementally.

```
smart-fin-coach/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API endpoints
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── plaid.py         # Bank connections
│   │   │   ├── transactions.py  # Transaction management
│   │   │   ├── budgets.py       # Budget tracking
│   │   │   ├── goals.py         # Goal management
│   │   │   ├── chat.py          # AI chatbot
│   │   │   └── insights.py      # Financial insights
│   │   ├── core/                # Core utilities
│   │   │   ├── database.py      # Database connection
│   │   │   ├── security.py      # Security & encryption
│   │   │   └── llm_client.py    # Gemini AI client
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py          # User model
│   │   │   ├── transaction.py   # Transaction model
│   │   │   ├── budget.py        # Budget model
│   │   │   ├── goal.py          # Goal model
│   │   │   └── insight.py       # Insight model
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── plaid_service.py # Plaid integration
│   │   │   ├── mcp_server.py    # AI tool registry
│   │   │   └── budget_service.py # Budget logic
│   │   └── main.py              # FastAPI application
│   ├── migrations/              # Database migrations
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
├── frontend/
│   ├── app/                     # Next.js pages
│   │   ├── dashboard/           # Dashboard page
│   │   ├── transactions/        # Transactions page
│   │   └── accounts/            # Accounts page
│   ├── components/              # React components
│   │   ├── chat/                # Chatbot components
│   │   ├── dashboard/           # Dashboard widgets
│   │   └── ui/                  # UI components
│   ├── lib/                     # Utilities
│   │   └── api.ts               # API client
│   ├── stores/                  # State management
│   │   └── authStore.ts         # Auth state
│   └── package.json             # Node dependencies
├── docker-compose.yml           # Docker services
└── README.md                    # This file
```

## Technologies

The technology stack was carefully selected to balance developer productivity with application performance and security. The backend uses FastAPI for its native async support and automatic API documentation generation, paired with SQLAlchemy 2.0's async capabilities for non-blocking database operations. The frontend leverages Next.js 14 with React 19 for server-side rendering and optimal performance, while TanStack Query handles sophisticated client-side caching and state synchronization. All components run in Docker containers for consistent development environments across different machines.

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - Async ORM for database operations
- **PostgreSQL** - Relational database
- **Redis** - Caching and session storage
- **Alembic** - Database migration tool
- **Plaid** - Banking API for account connections
- **Google Gemini** - AI-powered financial insights
- **Pydantic** - Data validation
- **JWT** - Token-based authentication

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **TanStack Query** - Data fetching & caching
- **Lucide Icons** - Modern icon library
- **shadcn/ui** - Beautiful UI components

##  Security Best Practices

Security is paramount when handling financial data, and Smart Financial Coach implements multiple layers of protection including JWT-based authentication, bcrypt password hashing, and field-level encryption for sensitive data like bank tokens. The application follows the principle of least privilege, with rate limiting on API endpoints to prevent abuse and CORS configuration to restrict which domains can access the API. Developers must take additional precautions to safeguard API keys and cryptographic secrets, never committing them to version control or sharing them in public channels.

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong SECRET_KEY** - Generate cryptographically secure keys
3. **Rotate API keys regularly** - Especially in production
4. **Use HTTPS in production** - Never send tokens over HTTP
5. **Keep dependencies updated** - Run `pip list --outdated` and `npm outdated`
6. **Use Plaid sandbox** - For development and testing
7. **Enable MFA** - Add extra security to user accounts

##  Troubleshooting

Common issues during development typically involve service dependencies, port conflicts, or misconfigured environment variables. The Docker containers for PostgreSQL and Redis must be running before starting the backend server, as the application depends on these services for database connections and caching. Port conflicts can occur if you have other applications using ports 3000, 8000, 5432, or 6379. Most configuration problems can be resolved by carefully reviewing the .env file to ensure all required API keys and connection strings are properly set.

### Backend won't start
- Check if PostgreSQL is running: `docker ps`
- Verify environment variables in `backend/.env`
- Check if port 8000 is available: `lsof -ti:8000`
- Review logs: Check terminal output for error messages

### Frontend won't start
- Clear Next.js cache: `rm -rf frontend/.next`
- Check if port 3000 is available: `lsof -ti:3000`
- Reinstall dependencies: `cd frontend && npm install`

### Database connection errors
- Restart PostgreSQL: `docker-compose restart postgres`
- Check DATABASE_URL in `.env` matches docker-compose.yml
- Run migrations: `cd backend && alembic upgrade head`

### Plaid connection fails
- Verify PLAID_CLIENT_ID and PLAID_SECRET in `.env`
- Ensure PLAID_ENV is set to "sandbox"
- Check Plaid dashboard for API status

### AI chatbot not responding
- Verify GEMINI_API_KEY in `.env`
- Check API quota at Google AI Studio
- Review backend logs for errors

##  Development Tips

### Creating a test user
```bash
# Use the registration endpoint
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","first_name":"Test","last_name":"User"}'
```

### Accessing the database
```bash
# Connect to PostgreSQL
docker exec -it smart-fin-coach-postgres-1 psql -U fincoach -d fincoach

# List tables
\dt

# Query users
SELECT email, first_name, created_at FROM users;

# Exit
\q
```

### Viewing logs
```bash
# Backend logs (if running in background)
tail -f /tmp/backend.log

# Frontend logs
# Check the terminal where npm run dev is running

# Docker logs
docker-compose logs postgres
docker-compose logs redis
```

##  Production Deployment

Deploying Smart Financial Coach to production requires several critical configuration changes to ensure security, reliability, and performance. Unlike development where services run on localhost, production deployments should use managed database services, secure HTTPS connections, and environment-specific API keys. Plaid requires a separate production approval process before you can access real banking data, and Google Gemini API usage should be monitored to stay within quota limits. The frontend can be deployed to platforms like Vercel or Netlify, while the backend typically runs on cloud infrastructure like AWS, Google Cloud, or DigitalOcean with proper load balancing and auto-scaling configured.

For production deployment, consider:

1. **Environment Configuration**
   - Set `DEBUG=false`
   - Set `ENVIRONMENT=production`
   - Use production database (not Docker)
   - Use strong, unique SECRET_KEY and ENCRYPTION_KEY

2. **Database**
   - Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
   - Enable SSL connections
   - Set up regular backups

3. **Plaid Configuration**
   - Switch PLAID_ENV to "production"
   - Complete Plaid production approval process
   - Use production credentials

4. **Frontend**
   - Build for production: `npm run build`
   - Deploy to Vercel, Netlify, or similar
   - Configure environment variables in platform

5. **Backend**
   - Deploy to cloud provider (AWS, GCP, DigitalOcean)
   - Use production ASGI server (Gunicorn + Uvicorn workers)
   - Set up reverse proxy (Nginx)
   - Configure SSL certificates

6. **Security**
   - Enable CORS for your production domain only
   - Use HTTPS everywhere
   - Set up monitoring and logging
   - Implement rate limiting
   - Regular security audits

##  Additional Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)


