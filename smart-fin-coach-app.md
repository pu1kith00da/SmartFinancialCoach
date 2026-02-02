# Project Spec: Smart Financial Coach AI

## 1. Project Overview

### 1.1 Vision Statement
An AI-powered financial advisor that transforms raw transaction data into proactive, behavioral-changing insights. The goal is to move beyond passive tracking into automated, personalized coaching that empowers users to take control of their financial lives and build lasting positive habits.

### 1.2 Target Audience
| Segment | Needs | Key Features |
|---------|-------|--------------|
| **Young Adults & Students** | Build good financial habits, understand money basics | Gamification, educational insights, peer comparisons |
| **Freelancers & Gig Workers** | Manage variable income, tax planning, irregular cash flow | Income smoothing, tax set-asides, emergency fund building |
| **General Users** | Clear spending visibility, actionable savings tips | Smart categorization, goal tracking, subscription management |

### 1.3 Core Value Propositions
1. **Automated Intelligence**: No manual entry—AI categorizes and analyzes automatically
2. **Behavioral Change**: Insights designed to create lasting habit improvements
3. **Personalized Coaching**: Advice tailored to individual circumstances, not generic tips
4. **Financial Clarity**: Complete visibility into spending patterns and financial health
5. **Proactive Alerts**: Get notified before problems occur, not after

---

## 2. Complete Feature Set

### 2.1 Account Management & Authentication

#### 2.1.1 User Registration & Onboarding
- **Email/Password Registration** with strong password requirements (min 12 chars, special chars, numbers)
- **OAuth 2.0 Social Login** (Google, Apple, Microsoft)
- **Multi-Factor Authentication (MFA)** via TOTP apps or SMS backup
- **Onboarding Flow**:
  1. Financial goals questionnaire (retirement, emergency fund, debt payoff, etc.)
  2. Income type selection (salaried, freelance, mixed)
  3. Risk tolerance assessment
  4. Spending personality quiz (spender, saver, balanced)
  5. Connect first bank account via Plaid

#### 2.1.2 Profile Management
- Personal information (name, email, phone, timezone)
- Notification preferences (email, push, SMS, in-app)
- Privacy settings (data sharing, analytics opt-in/out)
- Connected accounts management
- Session management (view active sessions, logout all devices)

#### 2.1.3 Security Features
- **Biometric Login**: Face ID / Touch ID for mobile
- **PIN Protection**: 6-digit PIN for quick access
- **Privacy Mode**: One-tap to blur all amounts (for public use)
- **Activity Log**: Complete audit trail of all account actions
- **Suspicious Activity Alerts**: Notify on unusual login attempts

---

### 2.2 Bank Account Integration (Plaid)

#### 2.2.1 Account Linking
- **Supported Account Types**:
  - Checking accounts
  - Savings accounts
  - Credit cards
  - Investment accounts (read-only balances)
  - Loans (mortgages, auto, personal, student)
- **Multi-Bank Support**: Link unlimited accounts from different institutions
- **Institution Search**: Search 11,000+ supported institutions
- **Link Health Monitoring**: Auto-detect broken connections, prompt re-authentication

#### 2.2.2 Data Synchronization
- **Real-time Webhooks**: Instant transaction updates via Plaid webhooks
- **Daily Full Sync**: Comprehensive nightly reconciliation
- **Manual Refresh**: User-triggered sync with rate limiting
- **Historical Import**: Import up to 24 months of transaction history
- **Balance Tracking**: Real-time available and current balances

#### 2.2.3 Manual Account Support
- **Cash Accounts**: Track cash spending manually
- **External Assets**: Real estate, vehicles, valuables
- **Manual Transactions**: Add transactions for non-linked accounts
- **Import CSV/OFX**: Bulk import from bank exports

---

### 2.3 Intelligent Transaction Management

#### 2.3.1 AI-Powered Categorization
- **Primary Categories** (20+):
  - Housing (Rent, Mortgage, Utilities, Maintenance)
  - Transportation (Gas, Public Transit, Rideshare, Parking, Auto Insurance)
  - Food & Dining (Groceries, Restaurants, Coffee Shops, Fast Food, Alcohol)
  - Shopping (Clothing, Electronics, Home Goods, Personal Care)
  - Entertainment (Streaming, Gaming, Events, Hobbies)
  - Health & Fitness (Medical, Pharmacy, Gym, Sports)
  - Travel (Flights, Hotels, Vacation Activities)
  - Financial (Bank Fees, Interest, Investments, Transfers)
  - Income (Salary, Freelance, Investments, Refunds, Gifts)
  - Education (Tuition, Books, Courses, Student Loans)
  - Subscriptions (Software, Media, Memberships)
  - Personal Care (Haircuts, Spa, Beauty)
  - Pets (Food, Vet, Supplies, Grooming)
  - Gifts & Donations (Charity, Presents)
  - Taxes (Federal, State, Property)
  - Childcare (Daycare, Activities, Education)
  - Miscellaneous

- **Sub-Category Learning**: AI learns user-specific sub-categories
- **Merchant Intelligence**: 
  - Merchant name cleaning ("AMZN*123ABC" → "Amazon")
  - Logo fetching for visual recognition
  - Merchant categorization database
- **Split Transactions**: Split single transactions across multiple categories
- **Category Rules**: User-defined rules for automatic categorization

#### 2.3.2 Transaction Enrichment
- **Location Tagging**: Geo-tag transactions when available
- **Receipt Matching**: OCR receipt photos and match to transactions
- **Note & Tags**: Add custom notes and tags to transactions
- **Attachment Storage**: Store receipts, warranties, invoices
- **Duplicate Detection**: Identify and merge duplicate transactions

#### 2.3.3 Transaction Search & Filtering
- **Full-Text Search**: Search by merchant, notes, amount, category
- **Advanced Filters**:
  - Date range (custom, presets: this week, month, quarter, year)
  - Amount range (min/max)
  - Category (multi-select)
  - Account (multi-select)
  - Transaction type (debit, credit, transfer)
  - Tags
- **Saved Filters**: Save commonly used filter combinations
- **Export**: CSV, PDF, Excel export with custom date ranges

---

### 2.4 AI-Powered Insights Engine

#### 2.4.1 Spending Pattern Analysis
- **Daily Digest**: 
  - Yesterday's spending summary
  - Notable transactions
  - Daily budget status
  
- **Weekly Report**:
  - Week-over-week spending comparison
  - Top spending categories
  - Achieved/missed mini-goals
  - Weekend vs. weekday patterns

- **Monthly Deep Dive**:
  - Complete spending breakdown with visualizations
  - Month-over-month trends
  - Category-by-category analysis
  - Savings rate calculation
  - Net worth change

#### 2.4.2 Anomaly Detection (ML-Powered)
- **Spending Spikes**: Alert when category spending exceeds 150% of average
  - *Example*: "Heads up! Your dining out spending is $340 this month—that's 2x your usual $170."
  
- **Unusual Transactions**: Flag transactions that don't fit user patterns
  - *Example*: "We noticed a $500 charge at 'ELECTRONICS WORLD' which is unusual for you. Was this expected?"
  
- **Price Increase Detection**: Notice when regular purchases cost more
  - *Example*: "Your Netflix subscription increased from $15.99 to $22.99 last month."

- **Timing Anomalies**: Detect unusual transaction timing
  - *Example*: "There's been activity on your card at 3 AM in a different city. Please verify this was you."

#### 2.4.3 Intelligent Nudges & Coaching
- **Behavioral Nudges** (AI-generated, context-aware):
  ```
  Nudge Types:
  1. SAVINGS_OPPORTUNITY: "You've spent $127 on coffee this month. 
     Making coffee at home 3 days a week could save you $1,200/year!"
  
  2. GOAL_MOTIVATION: "You're 73% to your vacation fund! At this rate, 
     you'll hit it 2 weeks early. Keep it up! 🎉"
  
  3. SPENDING_ALERT: "You've already used 80% of your dining budget 
     and we're only halfway through the month."
  
  4. SMART_SUGGESTION: "I noticed you have $500 sitting in checking. 
     Moving it to your high-yield savings could earn you $25/year."
  
  5. CELEBRATION: "Amazing! You've reduced your shopping spending by 
     30% this month. That's $150 saved!"
  
  6. HABIT_FORMATION: "You've tracked your spending for 7 days straight! 
     Building this habit is the first step to financial freedom."
  ```

- **Nudge Delivery Rules**:
  - Maximum 2 nudges per day (prevent notification fatigue)
  - Prioritize high-impact, actionable insights
  - Vary tone: encouraging, informative, celebratory
  - Never shame or judge spending choices
  - Include specific numbers and comparisons
  - Suggest concrete next actions

#### 2.4.4 Comparative Analytics
- **Personal Benchmarking**:
  - Compare current month to same month last year
  - Seasonal spending pattern recognition
  - Lifestyle inflation tracking over time

- **Peer Comparison** (Anonymous, Opt-in):
  - Compare spending ratios to similar demographics
  - "Users with similar income typically spend 25% on housing—you're at 35%"
  - Category percentile rankings

- **Savings Rate Leaderboard** (Gamification):
  - Opt-in anonymous rankings
  - Monthly savings challenges
  - Achievement badges

---

### 2.5 Budgeting System

#### 2.5.1 Budget Creation
- **AI-Suggested Budgets**:
  - Analyze 3 months of spending history
  - Suggest realistic category budgets based on patterns
  - Apply 50/30/20 rule recommendations (needs/wants/savings)
  - Adjust for irregular income users

- **Budget Types**:
  - **Fixed Budget**: Set amount per category per month
  - **Flexible Budget**: Percentage of income (great for variable income)
  - **Rollover Budget**: Unused amounts carry to next month
  - **Zero-Based Budget**: Every dollar assigned a job
  - **Envelope System**: Digital envelopes for cash-like budgeting

#### 2.5.2 Budget Tracking
- **Real-Time Progress**:
  - Visual progress bars per category
  - Color coding: Green (<75%), Yellow (75-90%), Red (>90%)
  - Remaining amount and days left in period
  
- **Budget Alerts**:
  - 50% spent notification
  - 80% spent warning
  - Budget exceeded alert
  - Customizable thresholds

- **Budget Analytics**:
  - Historical budget adherence scores
  - Over/under trends by category
  - Suggested budget adjustments

#### 2.5.3 Budget vs. Actual Reports
- Side-by-side comparison visualization
- Variance analysis with explanations
- Trend lines showing improvement over time
- Export for financial planning purposes

---

### 2.6 Financial Goals System

#### 2.6.1 Goal Types
- **Emergency Fund**:
  - Target: 3-6 months of expenses
  - Auto-calculate based on actual spending
  - Priority: Critical

- **Debt Payoff**:
  - Support for snowball and avalanche methods
  - Interest savings calculator
  - Payoff date projection
  - Linked to actual loan accounts

- **Savings Goals**:
  - Custom name and target amount
  - Target date with progress tracking
  - Photo/image for visual motivation
  - Examples: Vacation, Down Payment, New Car, Wedding

- **Retirement**:
  - Integration with investment account balances
  - Compound growth projections
  - Required monthly contribution calculator

- **Irregular Expenses**:
  - Annual expenses broken into monthly savings
  - Examples: Insurance premiums, holidays, car registration

#### 2.6.2 Goal Tracking & Forecasting
- **Progress Dashboard**:
  - Visual progress indicators (bars, charts)
  - Current amount vs. target
  - Projected completion date (AI-calculated)
  - Days remaining

- **Feasibility Analysis** (AI/ML):
  - "Based on your current savings rate of $450/month, you'll reach your $5,000 goal in 11 months—1 month behind schedule."
  - Scenario modeling: "If you reduce dining out by 20%, you'll hit your goal 3 weeks early."

- **Auto-Adjustment Suggestions**:
  - When goals are at risk, suggest specific cuts
  - Prioritize suggestions by impact and difficulty
  - Respect user preferences (never suggest cutting essentials)

#### 2.6.3 Goal Contributions
- **Manual Contributions**: Log one-time additions
- **Automatic Allocations**: Rules for allocating income to goals
- **Round-Up Savings**: Round transactions up, save the difference
- **Found Money**: Allocate windfalls (tax refunds, bonuses) to goals

---

### 2.7 Subscription & Recurring Charge Management

#### 2.7.1 Automatic Detection
- **Detection Methods**:
  - Interval analysis (28-31 day patterns)
  - Amount consistency (within 10% variance)
  - Merchant keyword matching (subscription, monthly, premium)
  - Plaid recurring transactions API

- **Detection Accuracy**:
  - Confidence scores (high/medium/low)
  - Manual confirmation for uncertain detections
  - Learning from user confirmations

#### 2.7.2 Subscription Dashboard ("The Burn List")
- **Subscription Cards**:
  - Service name and logo
  - Monthly/annual cost
  - Billing date and frequency
  - Category (Entertainment, Productivity, Health, etc.)
  - Last used date (if detectable)
  - Days until next charge

- **Total Subscription Cost**:
  - Monthly total
  - Annual total
  - Percentage of income

- **Unused Subscription Alerts**:
  - "You haven't used Spotify in 45 days but paid $10.99 last month"
  - "Your gym membership costs $50/month but you haven't been in 3 months"

#### 2.7.3 Gray Charge Detection
- **Free Trial Conversions**: "Heads up! Your Hulu free trial ends in 3 days and will charge $17.99"
- **Price Increases**: "Your Adobe subscription increased from $52.99 to $59.99"
- **Forgotten Services**: Identify services with no apparent usage
- **Duplicate Services**: "You're paying for both Spotify ($10.99) and Apple Music ($10.99)"

#### 2.7.4 Subscription Management Actions
- **Cancellation Reminders**: Set reminders before billing dates
- **Cancellation Links**: Direct links to cancellation pages (where available)
- **Pause Suggestions**: Suggest pausing vs. canceling seasonal services
- **Negotiation Tips**: AI-generated scripts for negotiating lower rates
- **Alternative Suggestions**: Cheaper alternatives for expensive services

---

### 2.8 Bill Management & Calendar

#### 2.8.1 Bill Tracking
- **Automatic Bill Detection**: Identify recurring bills from transactions
- **Manual Bill Entry**: Add bills manually with:
  - Name and payee
  - Amount (fixed or variable estimate)
  - Due date and frequency
  - Category
  - Auto-pay status
  - Linked account

#### 2.8.2 Bill Calendar
- **Calendar View**: 
  - Monthly calendar with bill due dates
  - Color coding by category or status
  - Running balance projection

- **List View**:
  - Upcoming bills sorted by due date
  - Overdue bills highlighted
  - Paid bills with checkmarks

#### 2.8.3 Bill Reminders
- **Reminder Options**:
  - 7 days before due
  - 3 days before due
  - 1 day before due
  - Day of due date
  - Custom reminder schedule

- **Delivery Channels**: Push, Email, SMS

#### 2.8.4 Cash Flow Forecasting
- **30-Day Projection**:
  - Starting balance
  - Expected income (salary dates, recurring deposits)
  - Expected bills and subscriptions
  - Projected daily balance
  - Low balance warnings

- **Paycheck Allocation**: 
  - Visualize how each paycheck will be allocated
  - Identify potential shortfalls before they happen

---

### 2.9 Income Management (Freelancer/Gig Worker Focus)

#### 2.9.1 Income Tracking
- **Income Categorization**:
  - Salary/wages
  - Freelance/contract
  - Gig economy (Uber, DoorDash, etc.)
  - Investments (dividends, capital gains)
  - Side hustle
  - Government benefits
  - Gifts/windfalls

- **Income Trends**:
  - Monthly income chart
  - Income source breakdown
  - Year-over-year comparison
  - Seasonality detection

#### 2.9.2 Variable Income Tools
- **Income Smoothing**:
  - Calculate average monthly income over 6-12 months
  - Set "baseline budget" based on lowest income months
  - Buffer recommendations for high-income months

- **Invoice Tracking** (Manual Entry):
  - Track outstanding invoices
  - Expected payment dates
  - Overdue invoice alerts

#### 2.9.3 Tax Management (US-Focused Initially)
- **Estimated Tax Calculator**:
  - Based on freelance income
  - Quarterly payment reminders
  - Set-aside recommendations (25-30%)

- **Tax Set-Aside Account**:
  - Automatic percentage allocation
  - Quarterly payment tracking
  - Integration with tax deadlines

- **Deduction Tracking**:
  - Flag potential business expenses
  - Category-based deduction reports
  - Export for tax preparation

---

### 2.10 Net Worth Tracking

#### 2.10.1 Asset Management
- **Linked Assets**:
  - Bank accounts (automatic via Plaid)
  - Investment accounts (automatic via Plaid)
  - Retirement accounts (401k, IRA—automatic)

- **Manual Assets**:
  - Real estate (home value via Zillow API or manual)
  - Vehicles (value via KBB API or manual)
  - Crypto wallets (manual entry)
  - Collectibles and valuables
  - Business ownership

#### 2.10.2 Liability Tracking
- **Linked Liabilities**:
  - Credit card balances (automatic)
  - Mortgages (automatic)
  - Auto loans (automatic)
  - Student loans (automatic)
  - Personal loans (automatic)

- **Manual Liabilities**:
  - Private loans
  - Owed to individuals
  - Tax obligations

#### 2.10.3 Net Worth Dashboard
- **Current Net Worth**: Assets - Liabilities
- **Net Worth Over Time**: Historical chart (monthly snapshots)
- **Asset Allocation**: Pie chart of asset types
- **Debt-to-Asset Ratio**: Health indicator
- **Monthly Net Worth Change**: Breakdown of contributors

---

### 2.11 Reports & Analytics

#### 2.11.1 Pre-Built Reports
- **Spending Report**:
  - By category (pie chart, bar chart)
  - By merchant (top 10)
  - By time (daily, weekly, monthly trends)
  - Discretionary vs. non-discretionary

- **Income Report**:
  - By source
  - Trends over time
  - Income vs. expenses overlay

- **Cash Flow Report**:
  - Money in vs. money out
  - Net cash flow trends
  - Account-by-account breakdown

- **Net Worth Report**:
  - Historical progression
  - Asset and liability breakdown
  - Growth rate calculations

- **Annual Summary**:
  - Year-in-review statistics
  - Top merchants
  - Biggest spending months
  - Total saved
  - Goals achieved

#### 2.11.2 Custom Reports
- **Report Builder**:
  - Select metrics
  - Choose date range
  - Apply filters
  - Select visualization type
  - Save custom reports

#### 2.11.3 Export Options
- **Formats**: PDF, CSV, Excel, JSON
- **Scheduling**: Weekly or monthly email reports
- **Sharing**: Secure sharing links for financial advisors/accountants

---

### 2.12 Notifications & Alerts System

#### 2.12.1 Alert Types
| Alert Category | Examples |
|----------------|----------|
| **Spending** | Budget threshold reached, large transaction, unusual activity |
| **Bills** | Upcoming due date, payment posted, payment failed |
| **Goals** | Milestone reached, goal at risk, goal achieved |
| **Accounts** | Low balance, large deposit, connection issues |
| **Subscriptions** | Free trial ending, price increase, renewal upcoming |
| **Security** | New login, password changed, suspicious activity |
| **Insights** | Daily nudge, weekly summary, monthly report ready |

#### 2.12.2 Delivery Channels
- **In-App**: Notification center with read/unread status
- **Push Notifications**: iOS and Android (with granular controls)
- **Email**: Digest options (immediate, daily, weekly)
- **SMS**: Critical alerts only (security, large transactions)

#### 2.12.3 Notification Preferences
- Global quiet hours
- Per-category enable/disable
- Threshold customization
- Frequency limits

---

### 2.13 Gamification & Engagement

#### 2.13.1 Achievement System
- **Badges**:
  - "First Steps" - Link first account
  - "Budget Master" - Stay under budget for a full month
  - "Savings Streak" - Save money 10 weeks in a row
  - "Subscription Slayer" - Cancel 3 unused subscriptions
  - "Goal Crusher" - Achieve first savings goal
  - "Debt Free" - Pay off a debt
  - "Consistent" - Log in 30 days straight
  - And 50+ more...

- **Levels**: 
  - Novice → Apprentice → Journeyman → Expert → Master → Grandmaster
  - XP earned through positive financial actions
  - Level unlocks (features, themes, insights)

#### 2.13.2 Challenges
- **Weekly Challenges**:
  - "No-Spend Weekend" - Don't spend on Saturday/Sunday
  - "Coffee at Home" - Avoid coffee shop purchases
  - "Pack Your Lunch" - No weekday restaurant spending

- **Monthly Challenges**:
  - "Subscription Audit" - Review all subscriptions
  - "Budget Adherence" - Stay under all category budgets
  - "Savings Sprint" - Save 10% more than usual

#### 2.13.3 Streaks & Progress
- **Savings Streaks**: Consecutive weeks/months with positive savings
- **Budget Streaks**: Consecutive months under budget
- **Check-in Streaks**: Daily app engagement
- **Streak Protections**: One "freeze" per month to protect streaks

---

### 2.14 Data Security & Privacy

#### 2.14.1 Data Encryption
- **At Rest**: AES-256 encryption for all stored data
- **In Transit**: TLS 1.3 for all API communications
- **Field-Level Encryption**: Extra encryption for SSN, account numbers
- **Key Management**: AWS KMS or similar for key rotation

#### 2.14.2 Authentication Security
- **Password Requirements**: Min 12 chars, complexity rules, breach checking
- **MFA Options**: TOTP apps, SMS (backup), hardware keys (FIDO2)
- **Session Management**: 
  - Configurable timeout (15 min - 7 days)
  - Force logout from other devices
  - Refresh token rotation

#### 2.14.3 Privacy Features
- **Data Minimization**: Only collect what's necessary
- **Anonymization**: Strip PII from analytics data
- **Privacy Mode**: Blur amounts in UI
- **Export Data**: Download all personal data (GDPR)
- **Delete Account**: Complete data deletion with confirmation
- **Third-Party Sharing**: Explicit opt-in only, clear disclosures

#### 2.14.4 Compliance
- **SOC 2 Type II**: Annual audit for security practices
- **GDPR**: European data protection compliance
- **CCPA**: California privacy law compliance
- **PCI DSS**: If handling raw card data (Plaid handles this)

---

### 2.15 Settings & Customization

#### 2.15.1 Display Settings
- **Theme**: Light, Dark, System, Custom colors
- **Currency**: Primary display currency with multi-currency support
- **Date Format**: MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD
- **Number Format**: Thousand separators, decimal places
- **Language**: English (US/UK), Spanish, French, German (future)
- **Accessibility**: High contrast, larger text, screen reader optimization

#### 2.15.2 Financial Settings
- **Fiscal Month Start**: 1st, 15th, or custom (for non-standard pay cycles)
- **Week Start**: Sunday or Monday
- **Default Categories**: Customize category visibility and order
- **Hide Accounts**: Exclude accounts from net worth or budgets

#### 2.15.3 AI/Insight Settings
- **Coaching Tone**: Encouraging, Direct, Minimal
- **Insight Frequency**: Multiple daily, Once daily, Weekly digest
- **Focus Areas**: Savings, Debt, Investing, General
- **Disable AI Features**: Option to use app without AI analysis

---

## 3. Technical Architecture

### 3.1 System Architecture Overview
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Web App       │  │   iOS App       │  │   Android App   │              │
│  │   (React/Next)  │  │   (React Native)│  │   (React Native)│              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           └───────────────────┬┴───────────────────┘                        │
│                               │ HTTPS/WSS                                    │
├───────────────────────────────┼─────────────────────────────────────────────┤
│                        API GATEWAY (Kong/AWS API Gateway)                    │
│                    Rate Limiting │ Auth │ Logging │ Caching                  │
├───────────────────────────────┼─────────────────────────────────────────────┤
│                          BACKEND LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Application                               │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │Auth Service │ │Transaction  │ │Insights     │ │Goals        │   │    │
│  │  │             │ │Service      │ │Engine       │ │Service      │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │Budget       │ │Subscription │ │Notification │ │Reports      │   │    │
│  │  │Service      │ │Service      │ │Service      │ │Service      │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                          AI/ML LAYER                                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                │
│  │ LLM Service     │ │ Anomaly         │ │ Forecasting     │                │
│  │ (OpenAI/Claude) │ │ Detection (ML)  │ │ Model (Prophet) │                │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────┤
│                          DATA LAYER                                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                │
│  │ PostgreSQL      │ │ Redis           │ │ S3/Blob Storage │                │
│  │ (Primary DB)    │ │ (Cache/Queue)   │ │ (Files/Receipts)│                │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────┤
│                          EXTERNAL SERVICES                                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                │
│  │ Plaid API       │ │ SendGrid        │ │ Firebase        │                │
│  │ (Banking)       │ │ (Email)         │ │ (Push Notifs)   │                │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Tech Stack

#### Backend
| Component | Technology | Justification |
|-----------|------------|---------------|
| Framework | FastAPI (Python 3.11+) | Async support, auto-docs, type hints |
| Database | PostgreSQL 15 | ACID compliance, JSON support, reliability |
| ORM | SQLAlchemy 2.0 + Alembic | Async support, migrations |
| Cache | Redis 7 | Session storage, rate limiting, queues |
| Task Queue | Celery + Redis | Background jobs (sync, reports, AI) |
| Auth | JWT + OAuth2 | Stateless, secure, industry standard |
| AI/LLM | OpenAI GPT-4 / Anthropic Claude | Natural language insights |
| ML | scikit-learn, Prophet | Anomaly detection, forecasting |

#### Frontend
| Component | Technology | Justification |
|-----------|------------|---------------|
| Framework | Next.js 14 (React 18) | SSR, app router, performance |
| Styling | Tailwind CSS + shadcn/ui | Rapid development, consistency |
| State | Zustand + React Query | Simple global state, server cache |
| Charts | Recharts / Tremor | React-native charting |
| Forms | React Hook Form + Zod | Validation, performance |
| Mobile | React Native (Expo) | Code sharing, rapid development |

#### Infrastructure
| Component | Technology | Justification |
|-----------|------------|---------------|
| Hosting | AWS / Vercel + Railway | Scalability, managed services |
| CI/CD | GitHub Actions | Automation, integration |
| Monitoring | Sentry + Datadog | Error tracking, APM |
| Logging | Structured JSON + ELK | Searchability, compliance |

---

## 4. Data Schema & Models

### 4.1 Core Database Schema

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(20) DEFAULT 'free'  -- free, premium, pro
);

CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'system',
    currency VARCHAR(3) DEFAULT 'USD',
    date_format VARCHAR(20) DEFAULT 'MM/DD/YYYY',
    week_start VARCHAR(10) DEFAULT 'sunday',
    fiscal_month_start INTEGER DEFAULT 1,
    privacy_mode BOOLEAN DEFAULT FALSE,
    coaching_tone VARCHAR(20) DEFAULT 'encouraging',
    insight_frequency VARCHAR(20) DEFAULT 'daily',
    notification_email BOOLEAN DEFAULT TRUE,
    notification_push BOOLEAN DEFAULT TRUE,
    notification_sms BOOLEAN DEFAULT FALSE
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP
);

-- Plaid Integration
CREATE TABLE plaid_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plaid_item_id VARCHAR(255) UNIQUE NOT NULL,
    plaid_access_token TEXT NOT NULL,  -- Encrypted
    institution_id VARCHAR(50),
    institution_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',  -- active, needs_reauth, error
    last_successful_sync TIMESTAMP,
    last_sync_error TEXT,
    consent_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plaid_item_id UUID REFERENCES plaid_items(id) ON DELETE SET NULL,
    plaid_account_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    official_name VARCHAR(255),
    type VARCHAR(50) NOT NULL,  -- checking, savings, credit, loan, investment, other
    subtype VARCHAR(50),
    mask VARCHAR(4),
    current_balance DECIMAL(15, 2),
    available_balance DECIMAL(15, 2),
    limit_amount DECIMAL(15, 2),  -- For credit cards
    currency VARCHAR(3) DEFAULT 'USD',
    is_manual BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,
    include_in_net_worth BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    plaid_transaction_id VARCHAR(255),
    amount DECIMAL(15, 2) NOT NULL,  -- Positive = expense, Negative = income
    date DATE NOT NULL,
    datetime TIMESTAMP,
    name VARCHAR(500) NOT NULL,  -- Original merchant name
    merchant_name VARCHAR(255),  -- Cleaned/enriched name
    merchant_logo_url VARCHAR(500),
    category_id UUID REFERENCES categories(id),
    subcategory VARCHAR(100),
    pending BOOLEAN DEFAULT FALSE,
    transaction_type VARCHAR(20),  -- debit, credit
    payment_channel VARCHAR(20),  -- online, in_store, other
    location JSONB,  -- {city, region, country, lat, lon}
    notes TEXT,
    tags VARCHAR(255)[],
    is_recurring BOOLEAN DEFAULT FALSE,
    is_subscription BOOLEAN DEFAULT FALSE,
    is_discretionary BOOLEAN,
    is_excluded BOOLEAN DEFAULT FALSE,  -- Exclude from budgets/reports
    is_transfer BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(plaid_transaction_id)
);

CREATE INDEX idx_transactions_user_date ON transactions(user_id, date DESC);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_name);

-- Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(7),  -- Hex color
    parent_id UUID REFERENCES categories(id),
    is_system BOOLEAN DEFAULT TRUE,  -- System vs user-created
    is_income BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE user_category_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    rule_type VARCHAR(20) NOT NULL,  -- merchant_contains, merchant_exact, amount_range
    rule_value JSONB NOT NULL,  -- {pattern: "AMZN"} or {min: 100, max: 500}
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Budgets
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    name VARCHAR(100),
    amount DECIMAL(15, 2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly',  -- weekly, monthly, yearly
    budget_type VARCHAR(20) DEFAULT 'fixed',  -- fixed, percentage, rollover
    percentage_of_income DECIMAL(5, 2),  -- If percentage type
    rollover_enabled BOOLEAN DEFAULT FALSE,
    rollover_max DECIMAL(15, 2),
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE budget_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id UUID REFERENCES budgets(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    budgeted_amount DECIMAL(15, 2) NOT NULL,
    spent_amount DECIMAL(15, 2) DEFAULT 0,
    rollover_amount DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(budget_id, period_start)
);

-- Goals
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    goal_type VARCHAR(50) NOT NULL,  -- emergency_fund, debt_payoff, savings, retirement
    target_amount DECIMAL(15, 2) NOT NULL,
    current_amount DECIMAL(15, 2) DEFAULT 0,
    target_date DATE,
    priority INTEGER DEFAULT 1,  -- 1 = highest
    status VARCHAR(20) DEFAULT 'active',  -- active, paused, completed, abandoned
    image_url VARCHAR(500),
    linked_account_id UUID REFERENCES accounts(id),  -- For debt payoff
    monthly_contribution DECIMAL(15, 2),  -- Planned contribution
    auto_contribute BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE goal_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID REFERENCES goals(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL,
    contribution_type VARCHAR(20),  -- manual, automatic, roundup, transfer
    transaction_id UUID REFERENCES transactions(id),
    notes TEXT,
    contributed_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    merchant_name VARCHAR(255),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    frequency VARCHAR(20) NOT NULL,  -- weekly, monthly, quarterly, yearly
    category_id UUID REFERENCES categories(id),
    next_billing_date DATE,
    last_billing_date DATE,
    status VARCHAR(20) DEFAULT 'active',  -- active, paused, cancelled, trial
    trial_ends_at DATE,
    detection_confidence DECIMAL(3, 2),  -- 0.00 to 1.00
    is_user_confirmed BOOLEAN DEFAULT FALSE,
    cancel_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscription_transactions (
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    PRIMARY KEY (subscription_id, transaction_id)
);

-- Bills
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    payee VARCHAR(255),
    amount DECIMAL(15, 2),
    amount_variable BOOLEAN DEFAULT FALSE,
    due_day INTEGER,  -- Day of month (1-31)
    frequency VARCHAR(20) DEFAULT 'monthly',
    category_id UUID REFERENCES categories(id),
    account_id UUID REFERENCES accounts(id),  -- Paid from
    autopay_enabled BOOLEAN DEFAULT FALSE,
    reminder_days INTEGER[] DEFAULT '{7, 3, 1}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bill_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_id UUID REFERENCES bills(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id),
    amount_paid DECIMAL(15, 2) NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, overdue, skipped
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI Insights
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,  -- spending_alert, savings_opportunity, goal_progress, anomaly
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,  -- Supporting data for the insight
    priority VARCHAR(20) DEFAULT 'normal',  -- low, normal, high, critical
    action_type VARCHAR(50),  -- view_transactions, adjust_budget, review_subscription
    action_data JSONB,  -- Data needed for the action
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    is_actionable BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_insights_user_created ON insights(user_id, created_at DESC);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB,
    channels VARCHAR(20)[] DEFAULT '{in_app}',  -- in_app, push, email, sms
    sent_at TIMESTAMP,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Achievements
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    xp_reward INTEGER DEFAULT 0,
    category VARCHAR(50),  -- savings, budgeting, engagement, goals
    criteria JSONB NOT NULL  -- Conditions to unlock
);

CREATE TABLE user_achievements (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, achievement_id)
);

CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    xp_total INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    achievements_count INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0
);

-- Net Worth Snapshots
CREATE TABLE net_worth_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    total_assets DECIMAL(15, 2) NOT NULL,
    total_liabilities DECIMAL(15, 2) NOT NULL,
    net_worth DECIMAL(15, 2) NOT NULL,
    breakdown JSONB,  -- {accounts: [{id, name, type, balance}]}
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, snapshot_date)
);

-- Audit Log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at DESC);
```

### 4.2 Pydantic Models (API Schemas)

```python
# Example Pydantic models for API validation
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from enum import Enum

class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class GoalType(str, Enum):
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PAYOFF = "debt_payoff"
    SAVINGS = "savings"
    RETIREMENT = "retirement"

class InsightType(str, Enum):
    SPENDING_ALERT = "spending_alert"
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    GOAL_PROGRESS = "goal_progress"
    ANOMALY = "anomaly"
    SUBSCRIPTION_ALERT = "subscription_alert"

# Request/Response Models
class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    amount: Decimal
    date: date
    name: str
    merchant_name: Optional[str]
    category: Optional[str]
    is_pending: bool
    notes: Optional[str]
    tags: List[str]

class InsightResponse(BaseModel):
    id: UUID
    type: InsightType
    title: str
    message: str
    priority: str
    action_url: Optional[str]
    created_at: datetime
    is_read: bool

class GoalCreate(BaseModel):
    name: str = Field(..., max_length=255)
    goal_type: GoalType
    target_amount: Decimal = Field(..., gt=0)
    target_date: Optional[date]
    monthly_contribution: Optional[Decimal]

class BudgetSummary(BaseModel):
    category: str
    budgeted: Decimal
    spent: Decimal
    remaining: Decimal
    percentage_used: float
    status: str  # on_track, warning, exceeded
```

---

## 5. API Specification

### 5.1 Authentication Endpoints
```
POST   /api/v1/auth/register          - Create new account
POST   /api/v1/auth/login             - Login, get tokens
POST   /api/v1/auth/logout            - Invalidate refresh token
POST   /api/v1/auth/refresh           - Refresh access token
POST   /api/v1/auth/forgot-password   - Send password reset email
POST   /api/v1/auth/reset-password    - Reset password with token
POST   /api/v1/auth/verify-email      - Verify email with token
POST   /api/v1/auth/mfa/setup         - Initialize MFA setup
POST   /api/v1/auth/mfa/verify        - Verify MFA code
DELETE /api/v1/auth/mfa               - Disable MFA
GET    /api/v1/auth/sessions          - List active sessions
DELETE /api/v1/auth/sessions/{id}     - Revoke specific session
DELETE /api/v1/auth/sessions          - Revoke all sessions
```

### 5.2 User Endpoints
```
GET    /api/v1/users/me               - Get current user profile
PATCH  /api/v1/users/me               - Update profile
DELETE /api/v1/users/me               - Delete account
GET    /api/v1/users/me/preferences   - Get user preferences
PATCH  /api/v1/users/me/preferences   - Update preferences
GET    /api/v1/users/me/stats         - Get gamification stats
GET    /api/v1/users/me/achievements  - Get unlocked achievements
GET    /api/v1/users/me/export        - Export all user data (GDPR)
```

### 5.3 Plaid/Account Endpoints
```
POST   /api/v1/plaid/link-token       - Create Plaid Link token
POST   /api/v1/plaid/exchange-token   - Exchange public token
GET    /api/v1/plaid/items            - List connected institutions
DELETE /api/v1/plaid/items/{id}       - Disconnect institution
POST   /api/v1/plaid/items/{id}/sync  - Force sync for item

GET    /api/v1/accounts               - List all accounts
GET    /api/v1/accounts/{id}          - Get account details
POST   /api/v1/accounts               - Create manual account
PATCH  /api/v1/accounts/{id}          - Update account settings
DELETE /api/v1/accounts/{id}          - Delete manual account
GET    /api/v1/accounts/{id}/transactions - Get account transactions
```

### 5.4 Transaction Endpoints
```
GET    /api/v1/transactions           - List transactions (paginated)
         Query params: start_date, end_date, account_id, category_id, 
                       merchant, min_amount, max_amount, tags, 
                       is_recurring, search, page, limit, sort
GET    /api/v1/transactions/{id}      - Get transaction details
PATCH  /api/v1/transactions/{id}      - Update transaction (category, notes, tags)
POST   /api/v1/transactions           - Create manual transaction
DELETE /api/v1/transactions/{id}      - Delete manual transaction
POST   /api/v1/transactions/{id}/split - Split transaction into multiple
GET    /api/v1/transactions/search    - Full-text search
GET    /api/v1/transactions/export    - Export transactions (CSV/PDF)
```

### 5.5 Category Endpoints
```
GET    /api/v1/categories             - List all categories
POST   /api/v1/categories             - Create custom category
PATCH  /api/v1/categories/{id}        - Update category
DELETE /api/v1/categories/{id}        - Delete custom category
GET    /api/v1/categories/rules       - List categorization rules
POST   /api/v1/categories/rules       - Create rule
DELETE /api/v1/categories/rules/{id}  - Delete rule
```

### 5.6 Budget Endpoints
```
GET    /api/v1/budgets                - List all budgets
GET    /api/v1/budgets/{id}           - Get budget details
POST   /api/v1/budgets                - Create budget
PATCH  /api/v1/budgets/{id}           - Update budget
DELETE /api/v1/budgets/{id}           - Delete budget
GET    /api/v1/budgets/summary        - Get budget summary for current period
GET    /api/v1/budgets/history        - Get historical budget performance
POST   /api/v1/budgets/suggest        - Get AI-suggested budgets
```

### 5.7 Goal Endpoints
```
GET    /api/v1/goals                  - List all goals
GET    /api/v1/goals/{id}             - Get goal details
POST   /api/v1/goals                  - Create goal
PATCH  /api/v1/goals/{id}             - Update goal
DELETE /api/v1/goals/{id}             - Delete goal
POST   /api/v1/goals/{id}/contribute  - Add contribution
GET    /api/v1/goals/{id}/forecast    - Get AI forecast for goal
GET    /api/v1/goals/{id}/suggestions - Get AI suggestions to reach goal faster
```

### 5.8 Subscription Endpoints
```
GET    /api/v1/subscriptions          - List detected subscriptions
GET    /api/v1/subscriptions/{id}     - Get subscription details
PATCH  /api/v1/subscriptions/{id}     - Update subscription (confirm, pause, etc.)
DELETE /api/v1/subscriptions/{id}     - Remove subscription
POST   /api/v1/subscriptions          - Add manual subscription
GET    /api/v1/subscriptions/summary  - Get total subscription cost summary
POST   /api/v1/subscriptions/scan     - Trigger subscription scan
```

### 5.9 Bill Endpoints
```
GET    /api/v1/bills                  - List all bills
GET    /api/v1/bills/{id}             - Get bill details
POST   /api/v1/bills                  - Create bill
PATCH  /api/v1/bills/{id}             - Update bill
DELETE /api/v1/bills/{id}             - Delete bill
GET    /api/v1/bills/calendar         - Get bills calendar view
GET    /api/v1/bills/upcoming         - Get upcoming bills
POST   /api/v1/bills/{id}/paid        - Mark bill as paid
```

### 5.10 Insights Endpoints
```
GET    /api/v1/insights               - List insights (paginated)
         Query params: type, priority, is_read, since
GET    /api/v1/insights/{id}          - Get insight details
POST   /api/v1/insights/{id}/read     - Mark insight as read
POST   /api/v1/insights/{id}/dismiss  - Dismiss insight
POST   /api/v1/insights/{id}/action   - Perform insight action
GET    /api/v1/insights/daily         - Get today's daily nudge
```

### 5.11 Analytics/Reports Endpoints
```
GET    /api/v1/analytics/spending     - Spending breakdown
         Query params: start_date, end_date, group_by (category, merchant, day, week, month)
GET    /api/v1/analytics/income       - Income breakdown
GET    /api/v1/analytics/cashflow     - Cash flow analysis
GET    /api/v1/analytics/net-worth    - Net worth history
GET    /api/v1/analytics/trends       - Spending trends over time
GET    /api/v1/analytics/forecast     - 30-day cash flow forecast
POST   /api/v1/analytics/simulate     - Simulate purchase impact
GET    /api/v1/analytics/compare      - Compare periods
GET    /api/v1/reports/monthly        - Monthly summary report
GET    /api/v1/reports/annual         - Annual summary report
POST   /api/v1/reports/custom         - Generate custom report
GET    /api/v1/reports/export/{id}    - Download generated report
```

### 5.12 Notification Endpoints
```
GET    /api/v1/notifications          - List notifications
POST   /api/v1/notifications/read     - Mark notifications as read
POST   /api/v1/notifications/read-all - Mark all as read
GET    /api/v1/notifications/settings - Get notification settings
PATCH  /api/v1/notifications/settings - Update notification settings
POST   /api/v1/notifications/test     - Send test notification
```

---

## 6. AI/ML Implementation Details

### 6.1 Insight Generation (LLM)

#### Prompt Engineering Strategy
```python
# System prompt for the financial coach
SYSTEM_PROMPT = """
You are a supportive, knowledgeable financial coach. Your role is to help users 
understand their spending and make better financial decisions.

Guidelines:
1. Be encouraging and non-judgmental - never shame users for their spending
2. Be specific - use actual numbers and percentages from the data
3. Be actionable - every insight should have a clear next step
4. Be concise - keep insights to 2-3 sentences max
5. Vary your tone - mix encouragement, gentle warnings, and celebrations
6. Personalize - reference the user's specific goals and patterns
7. Be honest - if data is insufficient, say so rather than guessing

Available insight types:
- SAVINGS_OPPORTUNITY: Identify areas where user could reduce spending
- SPENDING_ALERT: Warn about unusual or high spending
- GOAL_PROGRESS: Update on progress toward financial goals
- PATTERN_DETECTION: Highlight interesting spending patterns
- CELEBRATION: Celebrate positive financial behavior
- TIP: Provide educational financial tips relevant to user's situation
"""

# Few-shot examples for consistent output
FEW_SHOT_EXAMPLES = [
    {
        "input": {
            "type": "high_category_spending",
            "category": "Dining Out",
            "current_month": 450,
            "previous_month": 280,
            "monthly_average": 300
        },
        "output": {
            "type": "SPENDING_ALERT",
            "title": "Dining Out Trending Higher",
            "message": "You've spent $450 on dining out this month—50% more than your usual $300. "
                      "Consider cooking a few extra meals at home to get back on track. "
                      "Even 2 home-cooked dinners could save you $60!",
            "priority": "normal",
            "action": "view_dining_transactions"
        }
    },
    # ... more examples
]
```

#### Insight Generation Pipeline
```python
class InsightEngine:
    """
    Generates personalized financial insights using LLM.
    """
    
    async def generate_daily_insights(self, user_id: UUID) -> List[Insight]:
        """Generate 1-2 daily insights for a user."""
        
        # 1. Gather context
        context = await self._gather_user_context(user_id)
        
        # 2. Identify potential insight opportunities
        opportunities = await self._identify_opportunities(context)
        
        # 3. Prioritize and select top 2
        selected = self._prioritize_opportunities(opportunities)[:2]
        
        # 4. Generate natural language insights
        insights = []
        for opp in selected:
            insight = await self._generate_insight(opp, context)
            insights.append(insight)
        
        # 5. Deduplicate against recent insights
        insights = await self._deduplicate(user_id, insights)
        
        return insights
    
    async def _gather_user_context(self, user_id: UUID) -> UserContext:
        """Gather all relevant context for insight generation."""
        return UserContext(
            transactions_30d=await self.tx_repo.get_recent(user_id, days=30),
            transactions_90d=await self.tx_repo.get_recent(user_id, days=90),
            budgets=await self.budget_repo.get_active(user_id),
            goals=await self.goal_repo.get_active(user_id),
            subscriptions=await self.sub_repo.get_all(user_id),
            spending_by_category=await self.analytics.spending_by_category(user_id),
            user_preferences=await self.user_repo.get_preferences(user_id),
            recent_insights=await self.insight_repo.get_recent(user_id, days=7)
        )
    
    async def _generate_insight(self, opportunity: InsightOpportunity, context: UserContext) -> Insight:
        """Use LLM to generate natural language insight."""
        
        prompt = self._build_prompt(opportunity, context)
        
        response = await self.llm_client.chat(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *FEW_SHOT_EXAMPLES,
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return self._parse_insight_response(response, opportunity)
```

### 6.2 Anomaly Detection (ML)

#### Implementation using Isolation Forest
```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np

class AnomalyDetector:
    """
    Detects unusual transactions and spending patterns using Isolation Forest.
    """
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,  # Expect ~5% anomalies
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
    
    def detect_transaction_anomalies(
        self, 
        transactions: List[Transaction],
        user_patterns: UserPatterns
    ) -> List[AnomalyResult]:
        """
        Detect anomalous transactions based on user's historical patterns.
        """
        if len(transactions) < 50:
            return []  # Not enough data
        
        # Feature engineering
        features = self._extract_features(transactions, user_patterns)
        
        # Fit and predict
        scaled_features = self.scaler.fit_transform(features)
        predictions = self.model.fit_predict(scaled_features)
        scores = self.model.decision_function(scaled_features)
        
        # Identify anomalies
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                anomalies.append(AnomalyResult(
                    transaction=transactions[i],
                    anomaly_score=float(-score),  # Higher = more anomalous
                    reasons=self._explain_anomaly(transactions[i], user_patterns)
                ))
        
        return sorted(anomalies, key=lambda x: x.anomaly_score, reverse=True)
    
    def _extract_features(
        self, 
        transactions: List[Transaction],
        patterns: UserPatterns
    ) -> np.ndarray:
        """Extract features for anomaly detection."""
        features = []
        
        for tx in transactions:
            features.append([
                tx.amount,
                tx.amount / patterns.category_avg.get(tx.category, tx.amount),
                self._hour_of_day(tx.datetime),
                self._day_of_week(tx.date),
                self._is_weekend(tx.date),
                patterns.merchant_frequency.get(tx.merchant_name, 0),
                self._days_since_last_similar(tx, transactions)
            ])
        
        return np.array(features)
    
    def _explain_anomaly(
        self, 
        tx: Transaction, 
        patterns: UserPatterns
    ) -> List[str]:
        """Generate human-readable explanations for why transaction is anomalous."""
        reasons = []
        
        cat_avg = patterns.category_avg.get(tx.category, 0)
        if cat_avg > 0 and tx.amount > cat_avg * 2:
            reasons.append(f"Amount is {tx.amount/cat_avg:.1f}x your typical {tx.category} spend")
        
        if tx.merchant_name not in patterns.known_merchants:
            reasons.append("New merchant you haven't used before")
        
        if patterns.typical_hours and tx.datetime:
            hour = tx.datetime.hour
            if hour < patterns.typical_hours[0] or hour > patterns.typical_hours[1]:
                reasons.append("Transaction at unusual time")
        
        return reasons
```

### 6.3 Cash Flow Forecasting (Prophet)

```python
from prophet import Prophet
import pandas as pd

class CashFlowForecaster:
    """
    Forecasts future cash flow using Facebook Prophet.
    """
    
    def forecast_balance(
        self,
        user_id: UUID,
        days_ahead: int = 30
    ) -> CashFlowForecast:
        """
        Predict user's account balance for the next N days.
        """
        # Get historical daily balances
        history = await self._get_daily_balances(user_id, days=180)
        
        # Prepare data for Prophet
        df = pd.DataFrame({
            'ds': [h.date for h in history],
            'y': [h.balance for h in history]
        })
        
        # Add known future events (bills, subscriptions)
        future_events = await self._get_scheduled_events(user_id, days_ahead)
        
        # Configure and fit model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        # Add regressors for known events
        for event_type in ['bill', 'subscription', 'income']:
            model.add_regressor(event_type)
        
        model.fit(df)
        
        # Make predictions
        future = model.make_future_dataframe(periods=days_ahead)
        future = self._add_event_regressors(future, future_events)
        forecast = model.predict(future)
        
        return CashFlowForecast(
            daily_predictions=[
                DayPrediction(
                    date=row['ds'],
                    predicted_balance=row['yhat'],
                    lower_bound=row['yhat_lower'],
                    upper_bound=row['yhat_upper']
                )
                for _, row in forecast.tail(days_ahead).iterrows()
            ],
            low_balance_warnings=self._identify_low_balance_dates(forecast),
            confidence_interval=0.8
        )
    
    def goal_feasibility_analysis(
        self,
        goal: Goal,
        user_context: UserContext
    ) -> GoalFeasibility:
        """
        Analyze whether user is on track to meet their goal.
        """
        # Calculate current savings rate
        monthly_income = user_context.avg_monthly_income
        monthly_expenses = user_context.avg_monthly_expenses
        current_savings_rate = monthly_income - monthly_expenses
        
        # Calculate required savings rate
        remaining_amount = goal.target_amount - goal.current_amount
        days_remaining = (goal.target_date - date.today()).days
        months_remaining = max(days_remaining / 30, 1)
        required_monthly = remaining_amount / months_remaining
        
        # Calculate gap
        monthly_gap = required_monthly - current_savings_rate
        
        # Project completion date at current rate
        if current_savings_rate > 0:
            projected_months = remaining_amount / current_savings_rate
            projected_date = date.today() + timedelta(days=projected_months * 30)
        else:
            projected_date = None
        
        # Generate suggestions if behind
        suggestions = []
        if monthly_gap > 0:
            suggestions = await self._generate_savings_suggestions(
                user_context, 
                monthly_gap
            )
        
        return GoalFeasibility(
            on_track=monthly_gap <= 0,
            current_monthly_savings=current_savings_rate,
            required_monthly_savings=required_monthly,
            monthly_gap=monthly_gap,
            projected_completion_date=projected_date,
            original_target_date=goal.target_date,
            suggestions=suggestions
        )
```

### 6.4 Subscription Detection Algorithm

```python
class SubscriptionDetector:
    """
    Detects recurring subscriptions from transaction history.
    """
    
    SUBSCRIPTION_KEYWORDS = [
        'subscription', 'monthly', 'premium', 'plus', 'pro',
        'netflix', 'spotify', 'hulu', 'disney', 'hbo', 'apple',
        'amazon prime', 'youtube', 'membership', 'recurring'
    ]
    
    def detect_subscriptions(
        self,
        transactions: List[Transaction],
        min_occurrences: int = 2
    ) -> List[DetectedSubscription]:
        """
        Analyze transactions to detect recurring subscriptions.
        """
        # Group by merchant
        merchant_groups = self._group_by_merchant(transactions)
        
        detected = []
        
        for merchant, txs in merchant_groups.items():
            if len(txs) < min_occurrences:
                continue
            
            # Check for recurring pattern
            pattern = self._detect_recurring_pattern(txs)
            
            if pattern:
                confidence = self._calculate_confidence(txs, pattern)
                
                detected.append(DetectedSubscription(
                    merchant_name=merchant,
                    amount=pattern.typical_amount,
                    frequency=pattern.frequency,
                    next_billing_date=pattern.next_date,
                    confidence=confidence,
                    transactions=txs,
                    is_keyword_match=self._matches_keywords(merchant)
                ))
        
        return sorted(detected, key=lambda x: x.confidence, reverse=True)
    
    def _detect_recurring_pattern(
        self, 
        transactions: List[Transaction]
    ) -> Optional[RecurringPattern]:
        """
        Detect if transactions follow a recurring pattern.
        """
        if len(transactions) < 2:
            return None
        
        # Sort by date
        sorted_txs = sorted(transactions, key=lambda x: x.date)
        
        # Calculate intervals between transactions
        intervals = []
        for i in range(1, len(sorted_txs)):
            days = (sorted_txs[i].date - sorted_txs[i-1].date).days
            intervals.append(days)
        
        if not intervals:
            return None
        
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Determine frequency
        frequency = self._categorize_frequency(avg_interval)
        
        if frequency and std_interval < 5:  # Consistent timing
            amounts = [tx.amount for tx in transactions]
            avg_amount = np.mean(amounts)
            
            # Check amount consistency
            if np.std(amounts) / avg_amount < 0.15:  # Within 15% variance
                last_date = sorted_txs[-1].date
                next_date = last_date + timedelta(days=int(avg_interval))
                
                return RecurringPattern(
                    frequency=frequency,
                    typical_amount=Decimal(str(round(avg_amount, 2))),
                    avg_interval_days=avg_interval,
                    next_date=next_date
                )
        
        return None
    
    def _categorize_frequency(self, avg_days: float) -> Optional[str]:
        """Categorize interval into frequency type."""
        if 6 <= avg_days <= 8:
            return 'weekly'
        elif 13 <= avg_days <= 16:
            return 'biweekly'
        elif 28 <= avg_days <= 32:
            return 'monthly'
        elif 85 <= avg_days <= 95:
            return 'quarterly'
        elif 360 <= avg_days <= 370:
            return 'yearly'
        return None
    
    def _calculate_confidence(
        self, 
        transactions: List[Transaction],
        pattern: RecurringPattern
    ) -> float:
        """
        Calculate confidence score for subscription detection.
        """
        score = 0.0
        
        # More occurrences = higher confidence
        count_score = min(len(transactions) / 6, 1.0) * 0.3
        score += count_score
        
        # Consistent amounts = higher confidence
        amounts = [tx.amount for tx in transactions]
        amount_variance = np.std(amounts) / np.mean(amounts) if np.mean(amounts) > 0 else 1
        amount_score = max(0, 1 - amount_variance) * 0.3
        score += amount_score
        
        # Consistent timing = higher confidence
        timing_score = 0.2 if pattern.avg_interval_days else 0
        score += timing_score
        
        # Keyword match = higher confidence
        merchant = transactions[0].merchant_name or transactions[0].name
        if self._matches_keywords(merchant.lower()):
            score += 0.2
        
        return round(min(score, 1.0), 2)
```

---

## 7. Directory Structure (Detailed)

```
smart-fin-coach/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # CI pipeline (lint, test, build)
│   │   ├── cd-staging.yml            # Deploy to staging
│   │   ├── cd-production.yml         # Deploy to production
│   │   └── security-scan.yml         # Security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry
│   │   ├── config.py                 # Settings and configuration
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # Dependency injection
│   │   │   ├── router.py             # Main API router
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py           # Authentication endpoints
│   │   │       ├── users.py          # User management endpoints
│   │   │       ├── plaid.py          # Plaid integration endpoints
│   │   │       ├── accounts.py       # Account endpoints
│   │   │       ├── transactions.py   # Transaction endpoints
│   │   │       ├── categories.py     # Category endpoints
│   │   │       ├── budgets.py        # Budget endpoints
│   │   │       ├── goals.py          # Goal endpoints
│   │   │       ├── subscriptions.py  # Subscription endpoints
│   │   │       ├── bills.py          # Bill management endpoints
│   │   │       ├── insights.py       # AI insights endpoints
│   │   │       ├── analytics.py      # Analytics & reports endpoints
│   │   │       └── notifications.py  # Notification endpoints
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # Password hashing, JWT, encryption
│   │   │   ├── auth.py               # Authentication logic
│   │   │   ├── permissions.py        # Authorization & RBAC
│   │   │   ├── database.py           # Database connection & session
│   │   │   ├── redis.py              # Redis connection
│   │   │   ├── celery.py             # Celery configuration
│   │   │   ├── exceptions.py         # Custom exception classes
│   │   │   └── middleware.py         # Custom middleware (logging, etc.)
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base model with common fields
│   │   │   ├── user.py               # User, UserPreferences, Session
│   │   │   ├── plaid.py              # PlaidItem model
│   │   │   ├── account.py            # Account model
│   │   │   ├── transaction.py        # Transaction model
│   │   │   ├── category.py           # Category, CategoryRule models
│   │   │   ├── budget.py             # Budget, BudgetPeriod models
│   │   │   ├── goal.py               # Goal, GoalContribution models
│   │   │   ├── subscription.py       # Subscription model
│   │   │   ├── bill.py               # Bill, BillPayment models
│   │   │   ├── insight.py            # Insight model
│   │   │   ├── notification.py       # Notification model
│   │   │   ├── achievement.py        # Achievement, UserAchievement models
│   │   │   └── audit.py              # AuditLog model
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py             # Common response schemas
│   │   │   ├── auth.py               # Auth request/response schemas
│   │   │   ├── user.py               # User schemas
│   │   │   ├── account.py            # Account schemas
│   │   │   ├── transaction.py        # Transaction schemas
│   │   │   ├── budget.py             # Budget schemas
│   │   │   ├── goal.py               # Goal schemas
│   │   │   ├── subscription.py       # Subscription schemas
│   │   │   ├── bill.py               # Bill schemas
│   │   │   ├── insight.py            # Insight schemas
│   │   │   └── analytics.py          # Analytics/report schemas
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base repository class
│   │   │   ├── user.py               # User repository
│   │   │   ├── account.py            # Account repository
│   │   │   ├── transaction.py        # Transaction repository
│   │   │   ├── budget.py             # Budget repository
│   │   │   ├── goal.py               # Goal repository
│   │   │   ├── subscription.py       # Subscription repository
│   │   │   ├── bill.py               # Bill repository
│   │   │   └── insight.py            # Insight repository
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Authentication business logic
│   │   │   ├── user_service.py       # User management logic
│   │   │   ├── plaid_service.py      # Plaid API integration
│   │   │   ├── sync_service.py       # Transaction sync logic
│   │   │   ├── categorization_service.py  # Transaction categorization
│   │   │   ├── budget_service.py     # Budget calculations
│   │   │   ├── goal_service.py       # Goal tracking logic
│   │   │   ├── subscription_service.py    # Subscription management
│   │   │   ├── bill_service.py       # Bill management
│   │   │   ├── analytics_service.py  # Analytics calculations
│   │   │   ├── notification_service.py    # Notification sending
│   │   │   ├── export_service.py     # Data export (CSV, PDF)
│   │   │   └── gamification_service.py    # Achievements, XP, streaks
│   │   │
│   │   ├── ai_engine/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py         # OpenAI/Claude API client
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── system_prompts.py # System prompts for different contexts
│   │   │   │   ├── insight_prompts.py    # Insight generation prompts
│   │   │   │   └── few_shot_examples.py  # Few-shot examples for consistency
│   │   │   ├── insight_engine.py     # Insight generation logic
│   │   │   ├── anomaly_detector.py   # ML anomaly detection
│   │   │   ├── forecaster.py         # Cash flow forecasting (Prophet)
│   │   │   ├── subscription_detector.py  # Subscription detection
│   │   │   ├── categorizer.py        # AI-powered categorization
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── trained/          # Trained ML model files
│   │   │
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── sync_tasks.py         # Plaid sync background tasks
│   │       ├── insight_tasks.py      # Daily insight generation
│   │       ├── notification_tasks.py # Scheduled notifications
│   │       ├── report_tasks.py       # Report generation tasks
│   │       └── cleanup_tasks.py      # Data cleanup tasks
│   │
│   ├── migrations/
│   │   ├── versions/                 # Alembic migration files
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest fixtures
│   │   ├── factories/                # Test data factories
│   │   │   ├── __init__.py
│   │   │   ├── user_factory.py
│   │   │   ├── transaction_factory.py
│   │   │   └── ...
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_budget_service.py
│   │   │   ├── test_anomaly_detector.py
│   │   │   └── ...
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_auth_endpoints.py
│   │   │   ├── test_transaction_endpoints.py
│   │   │   └── ...
│   │   └── e2e/
│   │       └── ...
│   │
│   ├── scripts/
│   │   ├── seed_categories.py        # Seed default categories
│   │   ├── seed_achievements.py      # Seed achievements
│   │   ├── migrate_data.py           # Data migration scripts
│   │   └── generate_test_data.py     # Generate test data
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   └── pyproject.toml                # Python project config (black, isort, etc.)
│
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── icons/                    # App icons, PWA icons
│   │   └── images/                   # Static images
│   │
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── page.tsx              # Landing page
│   │   │   ├── globals.css           # Global styles
│   │   │   ├── (auth)/               # Auth route group
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── register/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── forgot-password/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── (dashboard)/          # Dashboard route group
│   │   │   │   ├── layout.tsx        # Dashboard layout with sidebar
│   │   │   │   ├── dashboard/
│   │   │   │   │   └── page.tsx      # Main dashboard
│   │   │   │   ├── transactions/
│   │   │   │   │   ├── page.tsx      # Transaction list
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx  # Transaction detail
│   │   │   │   ├── accounts/
│   │   │   │   │   └── page.tsx      # Account management
│   │   │   │   ├── budgets/
│   │   │   │   │   ├── page.tsx      # Budget overview
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx  # Budget detail
│   │   │   │   ├── goals/
│   │   │   │   │   ├── page.tsx      # Goals overview
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx  # Goal detail
│   │   │   │   ├── subscriptions/
│   │   │   │   │   └── page.tsx      # Subscription manager
│   │   │   │   ├── bills/
│   │   │   │   │   └── page.tsx      # Bill calendar
│   │   │   │   ├── insights/
│   │   │   │   │   └── page.tsx      # AI insights feed
│   │   │   │   ├── reports/
│   │   │   │   │   └── page.tsx      # Reports & analytics
│   │   │   │   ├── net-worth/
│   │   │   │   │   └── page.tsx      # Net worth tracker
│   │   │   │   └── settings/
│   │   │   │       ├── page.tsx      # Settings overview
│   │   │   │       ├── profile/
│   │   │   │       │   └── page.tsx
│   │   │   │       ├── security/
│   │   │   │       │   └── page.tsx
│   │   │   │       ├── notifications/
│   │   │   │       │   └── page.tsx
│   │   │   │       └── connected-accounts/
│   │   │   │           └── page.tsx
│   │   │   └── api/                  # API routes (if needed)
│   │   │       └── ...
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   └── ...
│   │   │   ├── layout/
│   │   │   │   ├── sidebar.tsx
│   │   │   │   ├── header.tsx
│   │   │   │   ├── footer.tsx
│   │   │   │   └── mobile-nav.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── stats-cards.tsx
│   │   │   │   ├── spending-chart.tsx
│   │   │   │   ├── recent-transactions.tsx
│   │   │   │   ├── budget-progress.tsx
│   │   │   │   ├── goal-progress.tsx
│   │   │   │   └── insight-card.tsx
│   │   │   ├── transactions/
│   │   │   │   ├── transaction-list.tsx
│   │   │   │   ├── transaction-row.tsx
│   │   │   │   ├── transaction-filters.tsx
│   │   │   │   ├── transaction-detail-modal.tsx
│   │   │   │   └── category-select.tsx
│   │   │   ├── budgets/
│   │   │   │   ├── budget-card.tsx
│   │   │   │   ├── budget-form.tsx
│   │   │   │   ├── budget-progress-bar.tsx
│   │   │   │   └── budget-vs-actual-chart.tsx
│   │   │   ├── goals/
│   │   │   │   ├── goal-card.tsx
│   │   │   │   ├── goal-form.tsx
│   │   │   │   ├── goal-progress-ring.tsx
│   │   │   │   └── contribution-modal.tsx
│   │   │   ├── subscriptions/
│   │   │   │   ├── subscription-card.tsx
│   │   │   │   ├── subscription-list.tsx
│   │   │   │   └── subscription-total.tsx
│   │   │   ├── charts/
│   │   │   │   ├── spending-pie-chart.tsx
│   │   │   │   ├── spending-trend-chart.tsx
│   │   │   │   ├── cash-flow-chart.tsx
│   │   │   │   ├── net-worth-chart.tsx
│   │   │   │   └── income-expense-chart.tsx
│   │   │   ├── insights/
│   │   │   │   ├── insight-feed.tsx
│   │   │   │   ├── insight-card.tsx
│   │   │   │   └── daily-nudge.tsx
│   │   │   ├── plaid/
│   │   │   │   ├── plaid-link-button.tsx
│   │   │   │   └── account-card.tsx
│   │   │   └── common/
│   │   │       ├── loading-spinner.tsx
│   │   │       ├── error-boundary.tsx
│   │   │       ├── empty-state.tsx
│   │   │       ├── confirm-dialog.tsx
│   │   │       ├── amount-display.tsx
│   │   │       ├── date-picker.tsx
│   │   │       └── search-input.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── use-auth.ts           # Authentication hook
│   │   │   ├── use-user.ts           # User data hook
│   │   │   ├── use-accounts.ts       # Accounts data hook
│   │   │   ├── use-transactions.ts   # Transactions hook
│   │   │   ├── use-budgets.ts        # Budgets hook
│   │   │   ├── use-goals.ts          # Goals hook
│   │   │   ├── use-subscriptions.ts  # Subscriptions hook
│   │   │   ├── use-insights.ts       # Insights hook
│   │   │   ├── use-analytics.ts      # Analytics hook
│   │   │   ├── use-plaid-link.ts     # Plaid Link hook
│   │   │   ├── use-privacy-mode.ts   # Privacy mode toggle
│   │   │   └── use-local-storage.ts  # Local storage hook
│   │   │
│   │   ├── store/
│   │   │   ├── index.ts              # Store exports
│   │   │   ├── auth-store.ts         # Auth state (Zustand)
│   │   │   ├── ui-store.ts           # UI state (sidebar, modals)
│   │   │   └── preferences-store.ts  # User preferences state
│   │   │
│   │   ├── lib/
│   │   │   ├── api-client.ts         # Axios/fetch client setup
│   │   │   ├── utils.ts              # Utility functions
│   │   │   ├── format.ts             # Formatting helpers (currency, date)
│   │   │   ├── validation.ts         # Zod schemas
│   │   │   ├── constants.ts          # App constants
│   │   │   └── plaid.ts              # Plaid Link setup
│   │   │
│   │   ├── types/
│   │   │   ├── index.ts              # Type exports
│   │   │   ├── user.ts               # User types
│   │   │   ├── account.ts            # Account types
│   │   │   ├── transaction.ts        # Transaction types
│   │   │   ├── budget.ts             # Budget types
│   │   │   ├── goal.ts               # Goal types
│   │   │   ├── subscription.ts       # Subscription types
│   │   │   ├── insight.ts            # Insight types
│   │   │   └── api.ts                # API response types
│   │   │
│   │   └── styles/
│   │       └── themes/               # Theme configurations
│   │
│   ├── tests/
│   │   ├── setup.ts
│   │   ├── components/               # Component tests
│   │   └── e2e/                      # Playwright E2E tests
│   │
│   ├── .env.local.example
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
│
├── mobile/                           # React Native (Expo) app
│   ├── app/                          # Expo Router
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── app.json
│   └── package.json
│
├── docs/
│   ├── api/                          # API documentation
│   ├── architecture/                 # Architecture decisions
│   ├── deployment/                   # Deployment guides
│   └── user-guide/                   # User documentation
│
├── scripts/
│   ├── setup.sh                      # Development setup script
│   ├── deploy.sh                     # Deployment script
│   └── backup.sh                     # Database backup script
│
├── docker-compose.yml                # Full stack Docker setup
├── docker-compose.dev.yml            # Development Docker setup
├── .gitignore
├── .env.example
├── LICENSE
├── README.md
└── smart_financial_coach.md          # This detailed specification file
```

---

## 8. Implementation Phases

### Phase 1: Foundation (Weeks 1-3)
**Goal:** Core infrastructure and authentication

#### Backend
- [ ] Project setup (FastAPI, PostgreSQL, Redis)
- [ ] Database schema creation and migrations
- [ ] User registration and authentication (JWT)
- [ ] Email verification flow
- [ ] Password reset functionality
- [ ] Basic user profile CRUD
- [ ] MFA implementation (TOTP)

#### Frontend
- [ ] Next.js project setup with Tailwind
- [ ] Authentication pages (login, register, forgot password)
- [ ] Protected route wrapper
- [ ] Basic dashboard layout (sidebar, header)
- [ ] Theme support (light/dark)

#### DevOps
- [ ] Docker development environment
- [ ] CI/CD pipeline setup
- [ ] Environment configuration

**Deliverables:**
- Working auth system
- Basic dashboard shell
- Development environment

---

### Phase 2: Banking Integration (Weeks 4-5)
**Goal:** Connect bank accounts and sync transactions

#### Backend
- [ ] Plaid integration service
- [ ] Link token generation endpoint
- [ ] Public token exchange endpoint
- [ ] Account model and endpoints
- [ ] Transaction model and endpoints
- [ ] Webhook handler for real-time updates
- [ ] Transaction sync background job
- [ ] Basic transaction categorization

#### Frontend
- [ ] Plaid Link integration
- [ ] Account connection flow
- [ ] Connected accounts list
- [ ] Transaction list with pagination
- [ ] Transaction detail modal
- [ ] Basic filtering (date, amount)
- [ ] Manual transaction entry

**Deliverables:**
- Bank account connection
- Transaction sync
- Transaction viewing/management

---

### Phase 3: Categorization & Organization (Weeks 6-7)
**Goal:** Smart categorization and transaction management

#### Backend
- [ ] Category management endpoints
- [ ] AI-powered categorization service
- [ ] Merchant name enrichment
- [ ] User-defined categorization rules
- [ ] Transaction splitting
- [ ] Tags system
- [ ] Search functionality (full-text)
- [ ] Export functionality (CSV)

#### Frontend
- [ ] Category management UI
- [ ] Transaction editing (category, notes, tags)
- [ ] Transaction search and advanced filters
- [ ] Split transaction modal
- [ ] Category rules UI
- [ ] Export transactions feature

**Deliverables:**
- Smart categorization
- Full transaction management
- Search and filtering

---

### Phase 4: Budgeting (Weeks 8-9)
**Goal:** Complete budgeting system

#### Backend
- [ ] Budget model and CRUD endpoints
- [ ] Budget period calculations
- [ ] AI-suggested budgets endpoint
- [ ] Budget vs. actual calculations
- [ ] Rollover budget logic
- [ ] Budget alerts/notifications
- [ ] Budget history tracking

#### Frontend
- [ ] Budget creation wizard
- [ ] Budget dashboard with progress bars
- [ ] Budget detail page
- [ ] AI budget suggestions UI
- [ ] Budget vs. actual charts
- [ ] Budget editing and deletion
- [ ] Budget alerts preferences

**Deliverables:**
- Full budgeting system
- AI recommendations
- Progress tracking

---

### Phase 5: Goals & Savings (Weeks 10-11)
**Goal:** Financial goals and savings tracking

#### Backend
- [ ] Goal model and CRUD endpoints
- [ ] Goal contribution tracking
- [ ] AI feasibility analysis
- [ ] Goal forecasting (Prophet)
- [ ] Savings suggestions engine
- [ ] Goal progress notifications
- [ ] Round-up savings calculation

#### Frontend
- [ ] Goal creation flow
- [ ] Goal dashboard with visual progress
- [ ] Goal detail page
- [ ] Contribution modal
- [ ] Feasibility analysis display
- [ ] Suggestions UI
- [ ] Goal completion celebration

**Deliverables:**
- Goal tracking system
- AI forecasting
- Savings recommendations

---

### Phase 6: Subscriptions & Bills (Weeks 12-13)
**Goal:** Recurring charge detection and bill management

#### Backend
- [ ] Subscription detection algorithm
- [ ] Subscription model and endpoints
- [ ] Free trial tracking
- [ ] Price change detection
- [ ] Bill model and CRUD endpoints
- [ ] Bill calendar calculations
- [ ] Bill reminders system
- [ ] Cash flow forecasting

#### Frontend
- [ ] Subscription dashboard ("Burn List")
- [ ] Subscription card components
- [ ] Subscription management actions
- [ ] Bill calendar view
- [ ] Bill list and creation
- [ ] Cash flow forecast visualization
- [ ] Bill reminder settings

**Deliverables:**
- Subscription detection
- Bill tracking
- Cash flow projections

---

### Phase 7: AI Insights Engine (Weeks 14-16)
**Goal:** Personalized AI coaching

#### Backend
- [ ] LLM integration (OpenAI/Claude)
- [ ] Prompt management system
- [ ] Insight generation pipeline
- [ ] Anomaly detection ML model
- [ ] Spending pattern analysis
- [ ] Insight prioritization logic
- [ ] Daily insight generation job
- [ ] Insight delivery (notifications)

#### Frontend
- [ ] Insight feed page
- [ ] Daily nudge component
- [ ] Insight cards with actions
- [ ] Insight preferences settings
- [ ] Anomaly alert UI
- [ ] Weekly/monthly insight summaries

**Deliverables:**
- AI-powered insights
- Anomaly detection
- Personalized coaching

---

### Phase 8: Analytics & Reports (Weeks 17-18)
**Goal:** Comprehensive financial analytics

#### Backend
- [ ] Analytics service (spending, income, cash flow)
- [ ] Net worth tracking
- [ ] Period comparison logic
- [ ] Report generation (PDF)
- [ ] Scheduled report delivery
- [ ] Custom report builder

#### Frontend
- [ ] Analytics dashboard
- [ ] Interactive charts (Recharts/Tremor)
- [ ] Net worth page
- [ ] Period comparison UI
- [ ] Report viewer
- [ ] Export and sharing

**Deliverables:**
- Full analytics suite
- Net worth tracking
- Exportable reports

---

### Phase 9: Gamification & Engagement (Week 19)
**Goal:** Engagement features to drive retention

#### Backend
- [ ] Achievement system
- [ ] XP and leveling calculations
- [ ] Streak tracking
- [ ] Challenge system
- [ ] Leaderboard (opt-in)

#### Frontend
- [ ] Achievement showcase
- [ ] Level progress display
- [ ] Streak indicators
- [ ] Challenge cards
- [ ] Badge collection

**Deliverables:**
- Achievement system
- Gamification elements

---

### Phase 10: Polish & Security (Weeks 20-21)
**Goal:** Production hardening

#### Backend
- [ ] Security audit fixes
- [ ] Rate limiting
- [ ] Input validation review
- [ ] Error handling improvements
- [ ] Performance optimization
- [ ] Logging and monitoring
- [ ] Data deletion (GDPR)

#### Frontend
- [ ] Accessibility audit (WCAG 2.1)
- [ ] Performance optimization
- [ ] Error boundaries
- [ ] Loading states
- [ ] Empty states
- [ ] Privacy mode
- [ ] Responsive testing

#### DevOps
- [ ] Production deployment
- [ ] SSL/TLS setup
- [ ] Backup automation
- [ ] Monitoring dashboards
- [ ] Alerting setup

**Deliverables:**
- Production-ready application
- Security compliance
- Monitoring in place

---

### Phase 11: Mobile App (Weeks 22-24)
**Goal:** React Native mobile application

- [ ] Expo project setup
- [ ] Shared component library
- [ ] Authentication screens
- [ ] Dashboard screen
- [ ] Transaction list
- [ ] Budget overview
- [ ] Goal tracking
- [ ] Push notifications
- [ ] Biometric authentication
- [ ] App Store / Play Store submission

**Deliverables:**
- iOS and Android apps

---

## 9. Success Metrics & KPIs

### User Engagement
| Metric | Target | Measurement |
|--------|--------|-------------|
| Daily Active Users (DAU) | 30% of registered | Analytics |
| Weekly Active Users (WAU) | 60% of registered | Analytics |
| Session Duration | > 3 minutes | Analytics |
| Feature Adoption | > 50% use 3+ features | Analytics |

### Behavioral Change
| Metric | Target | Measurement |
|--------|--------|-------------|
| Budget Adherence | 70% stay under budget | DB query |
| Savings Rate Improvement | +10% over 3 months | Historical comparison |
| Subscription Cancellations | 20% cancel unused | User actions |
| Goal Completion Rate | 40% achieve goals | Goal status |

### Technical Performance
| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | APM |
| Uptime | 99.9% | Monitoring |
| Error Rate | < 0.1% | Error tracking |
| Transaction Sync Latency | < 5 minutes | Logs |

### AI Quality
| Metric | Target | Measurement |
|--------|--------|-------------|
| Insight Relevance | 80% rated helpful | User feedback |
| Categorization Accuracy | 95% correct | User corrections |
| Anomaly Detection Precision | 90% true positives | User confirmations |
| Forecast Accuracy | Within 10% | Actual vs. predicted |

---

## 10. Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Plaid API changes | High | Abstract Plaid calls, version pinning |
| LLM cost overruns | Medium | Caching, rate limiting, model fallbacks |
| Database scaling | High | Indexing strategy, read replicas, partitioning |
| Security breach | Critical | Encryption, auditing, penetration testing |

### Business Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| User trust issues | High | Transparency, security certifications |
| Regulatory changes | Medium | Modular compliance, legal review |
| Competition | Medium | Unique AI features, superior UX |

---

## 11. Appendix

### A. Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/fincoach
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Plaid
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox  # sandbox, development, production

# AI
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Email
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@fincoach.app

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PLAID_ENV=sandbox
```

### B. Default Categories
```json
[
  {"name": "Housing", "icon": "home", "color": "#3B82F6", "subcategories": ["Rent", "Mortgage", "Utilities", "Maintenance", "Insurance"]},
  {"name": "Transportation", "icon": "car", "color": "#10B981", "subcategories": ["Gas", "Public Transit", "Rideshare", "Parking", "Auto Insurance", "Maintenance"]},
  {"name": "Food & Dining", "icon": "utensils", "color": "#F59E0B", "subcategories": ["Groceries", "Restaurants", "Coffee Shops", "Fast Food", "Alcohol"]},
  {"name": "Shopping", "icon": "shopping-bag", "color": "#EC4899", "subcategories": ["Clothing", "Electronics", "Home Goods", "Personal Care"]},
  {"name": "Entertainment", "icon": "film", "color": "#8B5CF6", "subcategories": ["Streaming", "Gaming", "Events", "Hobbies"]},
  {"name": "Health & Fitness", "icon": "heart", "color": "#EF4444", "subcategories": ["Medical", "Pharmacy", "Gym", "Sports"]},
  {"name": "Travel", "icon": "plane", "color": "#06B6D4", "subcategories": ["Flights", "Hotels", "Activities"]},
  {"name": "Financial", "icon": "dollar-sign", "color": "#6366F1", "subcategories": ["Bank Fees", "Interest", "Investments"]},
  {"name": "Income", "icon": "trending-up", "color": "#22C55E", "subcategories": ["Salary", "Freelance", "Investments", "Refunds"], "is_income": true},
  {"name": "Education", "icon": "book", "color": "#0EA5E9", "subcategories": ["Tuition", "Books", "Courses"]},
  {"name": "Subscriptions", "icon": "repeat", "color": "#A855F7", "subcategories": ["Software", "Media", "Memberships"]},
  {"name": "Gifts & Donations", "icon": "gift", "color": "#F97316", "subcategories": ["Charity", "Gifts"]},
  {"name": "Taxes", "icon": "file-text", "color": "#64748B", "subcategories": ["Federal", "State", "Property"]},
  {"name": "Pets", "icon": "paw", "color": "#84CC16", "subcategories": ["Food", "Vet", "Supplies"]},
  {"name": "Miscellaneous", "icon": "more-horizontal", "color": "#94A3B8", "subcategories": []}
]
```

### C. Achievement Definitions
```json
[
  {"code": "FIRST_LINK", "name": "Connected", "description": "Link your first bank account", "xp": 50, "category": "onboarding"},
  {"code": "BUDGET_CREATED", "name": "Planner", "description": "Create your first budget", "xp": 100, "category": "budgeting"},
  {"code": "GOAL_CREATED", "name": "Dreamer", "description": "Set your first financial goal", "xp": 100, "category": "goals"},
  {"code": "BUDGET_MASTER", "name": "Budget Master", "description": "Stay under budget for a full month", "xp": 250, "category": "budgeting"},
  {"code": "SAVINGS_STREAK_7", "name": "Saver", "description": "Save money 7 weeks in a row", "xp": 200, "category": "savings"},
  {"code": "SAVINGS_STREAK_30", "name": "Super Saver", "description": "Save money 30 weeks in a row", "xp": 500, "category": "savings"},
  {"code": "SUBSCRIPTION_SLAYER", "name": "Subscription Slayer", "description": "Cancel 3 unused subscriptions", "xp": 300, "category": "subscriptions"},
  {"code": "GOAL_ACHIEVED", "name": "Goal Crusher", "description": "Achieve a financial goal", "xp": 500, "category": "goals"},
  {"code": "DEBT_FREE", "name": "Debt Free", "description": "Pay off a debt completely", "xp": 1000, "category": "debt"},
  {"code": "STREAK_30", "name": "Consistent", "description": "Use the app for 30 days straight", "xp": 200, "category": "engagement"},
  {"code": "STREAK_100", "name": "Dedicated", "description": "Use the app for 100 days straight", "xp": 500, "category": "engagement"},
  {"code": "INSIGHTS_READ_50", "name": "Learner", "description": "Read 50 financial insights", "xp": 150, "category": "engagement"},
  {"code": "NET_WORTH_POSITIVE", "name": "In the Black", "description": "Achieve positive net worth", "xp": 1000, "category": "net_worth"}
]
```

---

**Document Version:** 1.0  
**Last Updated:** January 30, 2026  
**Author:** Smart Financial Coach Development Team

