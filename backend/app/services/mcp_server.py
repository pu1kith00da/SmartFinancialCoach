"""
MCP (Model Context Protocol) Server for AI Chatbot.
In-process tool registry that executes tools by calling service-layer methods directly.
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import AnalyticsService
from app.services.transaction_service import TransactionService
from app.services.insight_service import InsightService
from app.services.goal_service import goal_service
from app.schemas.transaction import TransactionFilterRequest

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP-style tool registry and execution engine.
    Calls internal service-layer methods directly (in-process).
    """
    
    def __init__(self, db: AsyncSession, user_id: UUID, llm_client):
        """
        Initialize MCP server.
        
        Args:
            db: Database session
            user_id: Current user ID
            llm_client: LLM client for chat with tools
        """
        self.db = db
        self.user_id = user_id
        self.llm_client = llm_client
        self.tools = self._register_tools()
        self.conversation_history: List[Dict[str, str]] = []
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all available tools with their schemas."""
        return {
            "get_dashboard_summary": {
                "description": "Get the same financial overview used by the dashboard (income, spending, savings rate, budgets, goals, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "list_transactions": {
                "description": "Retrieve transactions with filters (category, date range, search term, pagination)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max results (default 20)"},
                        "offset": {"type": "integer", "description": "Pagination offset"},
                        "start_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
                        "end_date": {"type": "string", "description": "End date YYYY-MM-DD"},
                        "category": {"type": "string", "description": "Filter by category"},
                        "search": {"type": "string", "description": "Search merchant/name"}
                    },
                    "required": []
                }
            },
            "get_spending_analytics": {
                "description": "Get spending analytics for a period (includes totals and by-category breakdown)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
                        "end_date": {"type": "string", "description": "End date YYYY-MM-DD"},
                        "compare": {"type": "boolean", "description": "Compare with previous period"}
                    },
                    "required": []
                }
            },
            "list_insights": {
                "description": "Get AI-generated financial insights including savings opportunities, spending alerts, and personalized recommendations. Use this when user asks about: 'how to save money', 'where can I save', 'evaluate my transactions', 'reduce spending', 'savings tips', 'financial advice', 'money saving opportunities', or wants analysis of their spending patterns. Returns actionable insights based on their actual transaction data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "Filter by insight type (e.g., 'savings_opportunity' for money-saving tips)"},
                        "priority": {"type": "string", "description": "Filter by priority"},
                        "category": {"type": "string", "description": "Filter by category"},
                        "limit": {"type": "integer", "description": "Max results (default 5)"}
                    },
                    "required": []
                }
            },
            "list_goals": {
                "description": "List financial goals and progress",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "Filter by status"},
                        "goal_type": {"type": "string", "description": "Filter by goal type"},
                        "limit": {"type": "integer", "description": "Max results"}
                    },
                    "required": []
                }
            },
            "get_spending_trends": {
                "description": "Get multi-month spending trends",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "months": {"type": "integer", "description": "Number of months (1-24)"}
                    },
                    "required": []
                }
            },
            "list_subscriptions": {
                "description": "Get user's active and inactive subscriptions with costs. Use when user asks about subscriptions, recurring charges, monthly costs, or what they're paying for.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "Filter by status: 'active', 'cancelled', 'paused'"},
                        "limit": {"type": "integer", "description": "Max results (default 20)"}
                    },
                    "required": []
                }
            },
            "list_budgets": {
                "description": "Get user's budgets with spending data for each category. Use when user asks about budgets, spending limits, how much they have left to spend, or wants budget recommendations. Categories: Groceries, Shopping, Food & Dining, Bills, Transportation, Other, Savings.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Convert tools to Gemini function calling format."""
        schemas = []
        for name, tool in self.tools.items():
            schemas.append({
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            })
        return schemas
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message using LLM with tools.
        
        Args:
            message: User's message
            
        Returns:
            Dict with response, tools_used, and data
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        tools_used = []
        tool_results = {}
        
        # Multi-step reasoning loop
        max_iterations = 5
        for i in range(max_iterations):
            logger.info(f"Processing iteration {i+1}/{max_iterations}")
            
            # Call LLM with tools
            response = await self.llm_client.chat_with_tools(
                messages=self.conversation_history,
                tools=self.get_tool_schemas()
            )
            
            # Check if LLM wants to use tools
            if response.get("tool_calls"):
                logger.info(f"LLM requested {len(response['tool_calls'])} tool calls")
                
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["arguments"]
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    try:
                        result = await self.execute_tool(tool_name, tool_args)
                        tools_used.append(tool_name)
                        tool_results[tool_name] = result
                        
                        # Add tool result to conversation
                        self.conversation_history.append({
                            "role": "function",
                            "name": tool_name,
                            "content": str(result)
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        self.conversation_history.append({
                            "role": "function",
                            "name": tool_name,
                            "content": f"Error: {str(e)}"
                        })
            else:
                # LLM has final answer
                final_response = response.get("content", "I'm sorry, I couldn't process that request.")
                
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                
                return {
                    "response": final_response,
                    "tools_used": list(set(tools_used)),
                    "data": tool_results
                }
        
        # Max iterations reached
        return {
            "response": "I apologize, but I need more information to answer your question. Could you please rephrase it?",
            "tools_used": list(set(tools_used)),
            "data": tool_results
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a registered tool by calling service-layer methods.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        if tool_name == "get_dashboard_summary":
            service = AnalyticsService(self.db)
            summary = await service.get_dashboard_summary(self.user_id)
            return {
                "net_worth": float(summary.net_worth),
                "monthly_income": float(summary.monthly_income),
                "monthly_expenses": float(summary.monthly_expenses),
                "savings_rate": float(summary.savings_rate)
            }
        
        elif tool_name == "list_transactions":
            service = TransactionService(self.db)
            
            # Parse date strings
            start_date = None
            end_date = None
            if parameters.get("start_date"):
                start_date = datetime.strptime(parameters["start_date"], "%Y-%m-%d").date()
            if parameters.get("end_date"):
                end_date = datetime.strptime(parameters["end_date"], "%Y-%m-%d").date()
            
            filters = TransactionFilterRequest(
                limit=parameters.get("limit", 20),
                offset=parameters.get("offset", 0),
                start_date=start_date,
                end_date=end_date,
                category=parameters.get("category"),
                search=parameters.get("search")
            )
            
            transactions, total = await service.get_transactions(self.user_id, filters)
            
            return {
                "total": total,
                "transactions": [
                    {
                        "name": t.name,
                        "amount": float(t.amount),
                        "category": t.category,
                        "date": t.date.isoformat(),
                        "merchant": t.merchant_name
                    }
                    for t in transactions[:10]  # Limit to 10 for LLM context
                ]
            }
        
        elif tool_name == "get_spending_analytics":
            service = AnalyticsService(self.db)
            
            # Default to current month if not specified
            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")
            
            if not start_date:
                now = datetime.utcnow()
                start_date = now.replace(day=1).date()
            else:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            
            if not end_date:
                end_date = datetime.utcnow().date()
            else:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            analytics = await service.get_spending_analytics(
                self.user_id,
                start_date,
                end_date,
                parameters.get("compare", False)
            )
            
            return {
                "total_spending": float(analytics.total_spending),
                "by_category": [
                    {"category": c.category, "amount": float(c.amount)}
                    for c in analytics.by_category[:10]
                ]
            }
        
        elif tool_name == "list_insights":
            service = InsightService(self.db)
            
            filters = {
                "type": parameters.get("type"),
                "priority": parameters.get("priority"),
                "category": parameters.get("category"),
                "limit": parameters.get("limit", 5),
                "is_dismissed": False
            }
            
            insights, total = await service.get_insights(self.user_id, filters)
            
            return {
                "total": total,
                "insights": [
                    {
                        "title": i.title,
                        "message": i.message,
                        "type": i.type if isinstance(i.type, str) else i.type.value,
                        "priority": i.priority if isinstance(i.priority, str) else i.priority.value,
                        "category": i.category if i.category else None
                    }
                    for i in insights
                ]
            }
        
        elif tool_name == "list_goals":
            goals, total, active_count, completed_count = await goal_service.list_goals(
                self.db,
                self.user_id,
                status=parameters.get("status"),
                goal_type=parameters.get("goal_type"),
                skip=0,
                limit=parameters.get("limit", 10)
            )
            
            goal_list = []
            recommendations = []
            
            for g in goals:
                # Calculate monthly contribution needed
                monthly_needed = 0.0
                if g.target_date and g.target_date > date.today():
                    remaining = float(g.target_amount) - float(g.current_amount)
                    months_left = ((g.target_date.year - date.today().year) * 12 + 
                                   (g.target_date.month - date.today().month))
                    if months_left > 0 and remaining > 0:
                        monthly_needed = remaining / months_left
                
                # Check if on track
                on_track = True
                if g.target_date:
                    total_days = (g.target_date - g.started_at).days
                    elapsed_days = (date.today() - g.started_at).days
                    if total_days > 0:
                        expected_progress = (elapsed_days / total_days) * 100
                        actual_progress = g.progress_percentage
                        on_track = actual_progress >= (expected_progress - 10)  # 10% tolerance
                
                goal_data = {
                    "name": g.name,
                    "type": g.type,
                    "target_amount": float(g.target_amount),
                    "current_amount": float(g.current_amount),
                    "progress_percentage": float(g.progress_percentage or 0),
                    "target_date": g.target_date.isoformat() if g.target_date else None,
                    "monthly_contribution_needed": monthly_needed,
                    "on_track": on_track,
                    "status": g.status
                }
                goal_list.append(goal_data)
                
                # Generate recommendations
                if not on_track and g.status == "active":
                    recommendations.append(f"'{g.name}' is behind schedule. Consider increasing monthly contributions to ${monthly_needed:.2f}")
                elif monthly_needed > 1000:
                    recommendations.append(f"'{g.name}' requires ${monthly_needed:.2f}/month. This may be challenging - consider extending the deadline.")
            
            return {
                "total": total,
                "active_count": active_count,
                "completed_count": completed_count,
                "goals": goal_list,
                "recommendations": recommendations
            }
        
        elif tool_name == "get_spending_trends":
            service = AnalyticsService(self.db)
            months = parameters.get("months", 6)
            end_date = datetime.utcnow().date()
            
            trends = []
            for i in range(months):
                month_end = end_date.replace(day=1) - timedelta(days=i*30)
                month_start = (month_end - timedelta(days=30)).replace(day=1)
                
                analytics = await service.get_spending_analytics(
                    self.user_id,
                    month_start,
                    month_end
                )
                
                trends.append({
                    "month": month_start.strftime("%Y-%m"),
                    "total": float(analytics.total_spending)
                })
            
            return {"trends": trends}
        
        elif tool_name == "list_subscriptions":
            from app.services.subscription_service import SubscriptionService
            from app.models.subscription import SubscriptionStatus
            
            service = SubscriptionService(self.db)
            
            # Parse status if provided
            status = None
            if parameters.get("status"):
                status_map = {
                    "active": SubscriptionStatus.ACTIVE,
                    "cancelled": SubscriptionStatus.CANCELLED,
                    "paused": SubscriptionStatus.PAUSED
                }
                status = status_map.get(parameters["status"].lower())
            
            subscriptions = await service.get_user_subscriptions(
                self.user_id,
                status=status,
                limit=parameters.get("limit", 20)
            )
            
            # Get stats too
            stats = await service.get_subscription_stats(self.user_id)
            
            # Helper to calculate monthly cost
            def get_monthly_cost(s):
                amount = float(s.amount)
                if s.billing_cycle == "monthly":
                    return amount
                elif s.billing_cycle == "yearly":
                    return amount / 12
                elif s.billing_cycle == "quarterly":
                    return amount / 3
                elif s.billing_cycle == "weekly":
                    return amount * 4.33
                else:
                    return amount
            
            return {
                "total_subscriptions": len(subscriptions),
                "monthly_cost": float(stats.total_monthly_cost),
                "annual_cost": float(stats.total_annual_cost),
                "subscriptions": [
                    {
                        "name": s.name,
                        "provider": s.service_provider or s.name,
                        "amount": float(s.amount),
                        "monthly_amount": get_monthly_cost(s),
                        "billing_cycle": s.billing_cycle,
                        "status": s.status,
                        "next_billing_date": s.next_billing_date.isoformat() if s.next_billing_date else None,
                        "category": s.category
                    }
                    for s in subscriptions
                ]
            }
        
        elif tool_name == "list_budgets":
            from app.services.budget_service import BudgetService
            
            service = BudgetService(self.db)
            summary = await service.get_budget_summary(self.user_id)
            
            # Convert Pydantic models to dictionaries
            budgets_dict = [b.model_dump() if hasattr(b, 'model_dump') else b for b in summary["budgets"]]
            
            # Include recommendations based on spending patterns
            recommendations = []
            
            # Analyze each budget
            for budget in summary["budgets"]:
                if budget.status == "exceeded":
                    recommendations.append(
                        f"You've exceeded your {budget.category} budget by ${budget.spent - budget.budgeted:.2f}. "
                        f"Consider reducing spending in this category or increasing the budget."
                    )
                elif budget.status == "warning":
                    remaining = budget.budgeted - budget.spent
                    recommendations.append(
                        f"You have ${remaining:.2f} left in your {budget.category} budget. "
                        f"Be mindful of your spending to stay within budget."
                    )
            
            # Check for categories without budgets
            defined_categories = {b.category for b in summary["budgets"]}
            standard_categories = {"Groceries", "Shopping", "Food & Dining", "Bills", "Transportation", "Other", "Savings"}
            missing_categories = standard_categories - defined_categories
            
            if missing_categories:
                recommendations.append(
                    f"Consider setting budgets for: {', '.join(missing_categories)}. "
                    f"This will help you track your spending better."
                )
            
            # Budget recommendations based on income (50/30/20 rule)
            if summary["total_budgeted"] == 0:
                recommendations.append(
                    "You haven't set any budgets yet. A common budgeting rule is the 50/30/20 rule: "
                    "50% for needs (groceries, bills, transportation), 30% for wants (dining, shopping), "
                    "and 20% for savings and debt payments."
                )
            
            return {
                "budgets": budgets_dict,
                "total_budgeted": summary["total_budgeted"],
                "total_spent": summary["total_spent"],
                "month": summary["month"],
                "recommendations": recommendations
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
