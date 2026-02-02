"""
LLM Client for generating AI-powered financial insights.
Supports both OpenAI and Anthropic models.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class LLMClient:
    """
    Client for interacting with LLM APIs (OpenAI/Anthropic/Gemini).
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use. If None, auto-detect from environment.
        """
        self.provider = provider or self._detect_provider()
        self.client = None
        
        if self.provider == LLMProvider.OPENAI:
            self._init_openai()
        elif self.provider == LLMProvider.ANTHROPIC:
            self._init_anthropic()
        elif self.provider == LLMProvider.GEMINI:
            self._init_gemini()
        else:
            logger.warning("No LLM provider configured. Insights will use fallback templates.")
    
    def _detect_provider(self) -> Optional[LLMProvider]:
        """Auto-detect which LLM provider is configured."""
        if os.getenv("OPENAI_API_KEY"):
            return LLMProvider.OPENAI
        elif os.getenv("ANTHROPIC_API_KEY"):
            return LLMProvider.ANTHROPIC
        elif os.getenv("GOOGLE_API_KEY"):
            return LLMProvider.GEMINI
        return None
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment")
                return
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"Initialized OpenAI client with model: {self.model}")
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import AsyncAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found in environment")
                return
            self.client = AsyncAnthropic(api_key=api_key)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            logger.info(f"Initialized Anthropic client with model: {self.model}")
        except ImportError:
            logger.error("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found in environment")
                return
            genai.configure(api_key=api_key)
            self.model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
            self.client = genai.GenerativeModel(self.model)
            logger.info(f"Initialized Gemini client with model: {self.model}")
        except ImportError:
            logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
    
    async def generate_insight(
        self,
        insight_type: str,
        context: Dict[str, Any],
        user_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized financial insight using LLM.
        
        Args:
            insight_type: Type of insight to generate
            context: Context data for the insight
            user_name: User's name for personalization
        
        Returns:
            Dict with 'title' and 'message' keys
        """
        if not self.client:
            return self._fallback_insight(insight_type, context)
        
        try:
            system_prompt = self._get_system_prompt()
            user_prompt = self._build_user_prompt(insight_type, context, user_name)
            
            if self.provider == LLMProvider.OPENAI:
                return await self._generate_openai(system_prompt, user_prompt)
            elif self.provider == LLMProvider.ANTHROPIC:
                return await self._generate_anthropic(system_prompt, user_prompt)
            elif self.provider == LLMProvider.GEMINI:
                return await self._generate_gemini(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_insight(insight_type, context)
    
    async def _generate_openai(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        """Generate insight using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return {
            "title": result.get("title", "Financial Insight"),
            "message": result.get("message", "")
        }
    
    async def _generate_anthropic(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        """Generate insight using Anthropic Claude."""
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        import json
        content = response.content[0].text
        # Try to parse as JSON, fall back to extracting from text
        try:
            result = json.loads(content)
            return {
                "title": result.get("title", "Financial Insight"),
                "message": result.get("message", content)
            }
        except json.JSONDecodeError:
            # Extract title from first line if present
            lines = content.strip().split('\n', 1)
            return {
                "title": lines[0][:100] if lines else "Financial Insight",
                "message": lines[1] if len(lines) > 1 else content
            }
    
    async def _generate_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        """Generate insight using Google Gemini."""
        import json
        import re
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Gemini SDK doesn't have async support yet, so we use sync
        import asyncio
        response = await asyncio.to_thread(
            self.client.generate_content,
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Check if response was blocked or incomplete
        if not response.text or len(response.text.strip()) < 20:
            logger.warning(f"Gemini response too short or blocked. Candidates: {response.candidates}")
            logger.warning(f"Prompt feedback: {response.prompt_feedback}")
            # Return fallback
            raise Exception("Gemini response blocked or incomplete")
        
        content = response.text.strip()
        logger.debug(f"Raw Gemini response length: {len(content)}, first 200 chars: {content[:200]}")
        
        # Remove markdown code blocks if present (multiline)
        content = re.sub(r'^```(?:json)?\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n\s*```$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        logger.debug(f"Cleaned content length: {len(content)}, first 200 chars: {content[:200]}")
        
        # Try to parse as JSON, fall back to extracting from text
        try:
            result = json.loads(content)
            logger.debug(f"Successfully parsed JSON: title='{result.get('title')}', message length={len(result.get('message', ''))}")
            return {
                "title": result.get("title", "Financial Insight"),
                "message": result.get("message", content)
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}. Full content: {content}")
            # Return fallback instead of broken partial data
            raise Exception(f"Failed to parse Gemini JSON response: {e}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the financial coach."""
        return """You are a helpful financial coach providing personalized insights.

Respond ONLY with valid JSON in this format (no markdown, no code blocks):
{"title": "Brief title under 50 chars", "message": "Your 2-3 sentence insight under 250 chars"}

Be specific with numbers, encouraging in tone, and actionable."""
    
    async def generate_savings_recommendations(
        self,
        transactions: str,
        user_name: str = "there"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered money-saving recommendations from transaction data.
        
        Args:
            transactions: Formatted string of transaction summary by category
            user_name: User's first name for personalization
            
        Returns:
            Dict with 'recommendations' list containing title, message, category, etc.
        """
        system_prompt = """You are an expert financial advisor. Analyze the spending data and generate EXACTLY 10 SPECIFIC recommendations.

RULES:
1. MUST cite actual merchants from the data (e.g., "McDonald's", "Shell", "Uber")
2. MUST include exact dollar amounts (e.g., "$127.50", "$82.97")
3. MUST mention visit/transaction counts (e.g., "12 visits", "8 transactions")
4. NO generic advice - every recommendation must reference their actual data

EXAMPLE - If data shows "Shell: $236.80 (15x)", output:
{
  "title": "Optimize Shell fuel costs",
  "message": "You spent $236.80 at Shell (15 visits). Using GasBuddy app or fuel rewards cards could save 5-10¢/gallon, about $15/month.",
  "category": "Transportation",
  "potential_savings": 15.00,
  "type": "better_alternative"
}

EXAMPLE - If data shows "Starbucks: $127.50 (12x)", output:
{
  "title": "Cut Starbucks frequency",  
  "message": "You visited Starbucks 12 times spending $127.50. Reducing to 8 visits monthly saves $42. Try home brewing 4 days/week.",
  "category": "Food & Dining",
  "potential_savings": 42.00,
  "type": "reduce_spending"
}

Respond with valid JSON only:
{
  "recommendations": [ /* array of 10 objects like examples above */ ]
}"""

        user_prompt = f"""USER: {user_name}

{transactions}

Using the SPECIFIC merchants, amounts, and frequencies shown above, generate 10 personalized recommendations. Each must cite actual data (merchant names, dollar amounts, visit counts from above)."""

        try:
            if self.provider == LLMProvider.GEMINI:
                result = await self._generate_gemini_recommendations(system_prompt, user_prompt)
            elif self.provider == LLMProvider.OPENAI:
                result = await self._generate_openai_recommendations(system_prompt, user_prompt)
            elif self.provider == LLMProvider.ANTHROPIC:
                result = await self._generate_anthropic_recommendations(system_prompt, user_prompt)
            else:
                # Fallback recommendations
                result = self._get_fallback_recommendations()
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating savings recommendations: {e}")
            return self._get_fallback_recommendations()
    
    async def _generate_gemini_recommendations(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate recommendations using Google Gemini."""
        import json
        import re
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        import asyncio
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = await asyncio.to_thread(
            self.client.generate_content,
            full_prompt,
            generation_config={
                "temperature": 1.0,
                "max_output_tokens": 4096,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        if not response.text or len(response.text.strip()) < 20:
            raise Exception("Gemini response blocked or too short")
        
        content = response.text.strip()
        
        logger.debug(f"Raw Gemini response length: {len(content)}, first 200 chars: {content[:200]}")
        
        # Remove markdown code blocks
        content = re.sub(r'^```(?:json)?\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n\s*```$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        logger.debug(f"Cleaned content length: {len(content)}, first 200 chars: {content[:200]}")
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}. Full content: {content}")
            raise Exception(f"Failed to parse Gemini JSON response: {e}")
        
        # Ensure we have recommendations array
        if 'recommendations' not in result or not isinstance(result['recommendations'], list):
            logger.error(f"Invalid response format. Got: {result}")
            raise Exception("Invalid response format: missing recommendations array")
        
        # Validate each recommendation has required fields
        for i, rec in enumerate(result['recommendations']):
            if not isinstance(rec, dict):
                raise Exception(f"Recommendation {i} is not a dictionary")
            if 'title' not in rec or 'message' not in rec:
                logger.warning(f"Recommendation {i} missing required fields: {rec}")
        
        return result
    
    async def _generate_openai_recommendations(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate recommendations using OpenAI."""
        import json
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_anthropic_recommendations(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate recommendations using Anthropic."""
        import json
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        content = response.content[0].text
        return json.loads(content)
    
    def _get_fallback_recommendations(self) -> Dict[str, Any]:
        """Provide fallback recommendations when AI is unavailable."""
        return {
            "recommendations": [
                {
                    "title": "Review Subscription Services",
                    "message": "Check for unused subscriptions or services you can downgrade. Many people save $20-50/month by auditing their recurring charges.",
                    "category": "Subscriptions",
                    "potential_savings": 35.00,
                    "type": "eliminate_subscription"
                },
                {
                    "title": "Reduce Dining Out Frequency",
                    "message": "Try meal prepping once a week to reduce restaurant visits. Even cutting dining out by 25% can save hundreds monthly.",
                    "category": "Food & Dining",
                    "potential_savings": 75.00,
                    "type": "reduce_spending"
                },
                {
                    "title": "Compare Shopping Options",
                    "message": "Before large purchases, compare prices across different retailers and look for discount codes. You could save 10-15% on average.",
                    "category": "Shopping",
                    "potential_savings": 50.00,
                    "type": "better_alternative"
                }
            ]
        }
    
    def _build_user_prompt(
        self,
        insight_type: str,
        context: Dict[str, Any],
        user_name: Optional[str]
    ) -> str:
        """Build the user prompt with context."""
        greeting = user_name or "the user"
        
        # Type-specific prompts for better results
        prompts = {
            "spending_alert": self._build_spending_prompt(greeting, context),
            "budget_alert": self._build_budget_prompt(greeting, context),
            "goal_progress": self._build_goal_prompt(greeting, context),
            "goal_behind": self._build_goal_behind_prompt(greeting, context),
            "savings_opportunity": self._build_savings_prompt(greeting, context),
            "anomaly": self._build_anomaly_prompt(greeting, context)
        }
        
        return prompts.get(insight_type, self._build_generic_prompt(greeting, insight_type, context))
    
    def _build_spending_prompt(self, user: str, ctx: Dict) -> str:
        return f"""Generate a spending insight for {user}.

Data:
- Category: {ctx.get('category', 'Unknown')}
- Amount: ${ctx.get('amount', 0):.2f}
- Percentage of total: {ctx.get('percentage', 0):.1f}%
- Daily average: ${ctx.get('daily_average', 0):.2f}

Create a friendly insight that:
1. Acknowledges their spending in this category
2. Provides context (is this high, normal, or low?)
3. Suggests one specific action they could take
4. Keeps a supportive, non-judgmental tone

Response in JSON format."""

    def _build_budget_prompt(self, user: str, ctx: Dict) -> str:
        over_amount = ctx.get('over_amount', 0)
        
        return f"""Budget alert: {ctx.get('category')} - ${ctx.get('spent', 0):.0f} spent of ${ctx.get('budgeted', 0):.0f} budget ({ctx.get('percentage', 0):.0f}% used).
{f"Over by ${over_amount:.0f}." if over_amount > 0 else "Approaching limit."}

Generate encouraging insight with actionable tip. JSON only, no markdown."""

    def _build_goal_prompt(self, user: str, ctx: Dict) -> str:
        return f"""Generate a goal progress celebration for {user}.

Data:
- Goal: {ctx.get('goal_name', 'Your goal')}
- Progress: {ctx.get('progress_percentage', 0):.1f}%
- Current: ${ctx.get('current_amount', 0):.2f}
- Target: ${ctx.get('target_amount', 0):.2f}
- On track: {'Yes' if ctx.get('is_on_track', False) else 'No'}

Create an encouraging insight that:
1. Celebrates their progress
2. Mentions the specific percentage or milestone
3. Motivates them to keep going
4. Keeps tone positive and energizing

Response in JSON format."""

    def _build_goal_behind_prompt(self, user: str, ctx: Dict) -> str:
        return f"""Generate a goal adjustment insight for {user}.

Data:
- Goal: {ctx.get('goal_name', 'Your goal')}
- Progress: {ctx.get('progress_percentage', 0):.1f}%
- Current: ${ctx.get('current_amount', 0):.2f}
- Target: ${ctx.get('target_amount', 0):.2f}
- Status: Behind schedule

Create a supportive insight that:
1. Acknowledges they're behind schedule
2. Avoids blame or judgment
3. Suggests ONE concrete action to get back on track
4. Maintains optimism about reaching the goal

Response in JSON format."""

    def _build_savings_prompt(self, user: str, ctx: Dict) -> str:
        return f"""Generate a savings opportunity insight for {user}.

Data:
- Total spending: ${ctx.get('total_spending', 0):.2f}
- Potential savings: ${ctx.get('potential_savings', 0):.2f}
- Suggestion area: {ctx.get('suggestion', 'general spending')}

Create an insight that:
1. Highlights the savings opportunity
2. Provides specific numbers
3. Suggests where they could reduce spending
4. Makes it feel achievable, not restrictive

Response in JSON format."""

    def _build_anomaly_prompt(self, user: str, ctx: Dict) -> str:
        return f"""Generate an anomaly alert for {user}.

Data:
- Amount: ${ctx.get('amount', 0):.2f}
- Merchant: {ctx.get('merchant', 'Unknown')}
- Category: {ctx.get('category', 'Unknown')}
- Date: {ctx.get('date', 'Recently')}

This transaction is unusually large. Create an alert that:
1. Points out the unusual transaction
2. Asks if they recognize it (fraud prevention)
3. Suggests reviewing the transaction
4. Keeps a helpful, non-alarming tone

Response in JSON format."""

    def _build_generic_prompt(self, user: str, insight_type: str, context: Dict) -> str:
        """Generic fallback prompt."""
        prompt = f"Generate a {insight_type} insight for {user} based on this data:\n\n"
        
        for key, value in context.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += "\nGenerate a helpful, actionable insight in JSON format."
        return prompt
    
    def _fallback_insight(self, insight_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback insight when LLM is unavailable."""
        templates = {
            "spending_alert": {
                "title": "Spending Higher Than Usual",
                "message": "Your {category} spending is ${amount} this month, which is higher than usual. Consider reviewing recent transactions."
            },
            "budget_alert": {
                "title": "{category} Budget Alert",
                "message": "You've spent ${spent} of your ${budgeted} {category} budget ({percentage}% used). {action}"
            },
            "goal_progress": {
                "title": "Goal Progress Update",
                "message": "You're making progress on your financial goals. Keep up the great work!"
            },
            "goal_behind": {
                "title": "Goal Check-In",
                "message": "Your goal needs attention. Consider adjusting your budget to get back on track."
            },
            "savings_opportunity": {
                "title": "Savings Opportunity",
                "message": "You've spent ${amount} on {category} this month. Small changes could help you save more."
            },
            "anomaly": {
                "title": "Unusual Transaction",
                "message": "We noticed an unusual transaction of ${amount}. Make sure everything looks correct."
            }
        }
        
        template = templates.get(insight_type, {
            "title": "Financial Insight",
            "message": "Review your spending patterns to find opportunities for improvement."
        })
        
        # Format context data for better messages
        formatted_context = context.copy()
        if 'over_amount' in formatted_context:
            over = formatted_context['over_amount']
            if over > 0:
                formatted_context['action'] = f"You're over by ${over:.0f}. Try to reduce spending in this category."
            else:
                formatted_context['action'] = "You're doing well staying within budget!"
        
        # Format numeric values
        for key, value in list(formatted_context.items()):
            if isinstance(value, float):
                formatted_context[key] = f"{value:.0f}"
        
        # Simple template variable replacement with safe fallback
        title = template["title"]
        message = template["message"]
        
        # Replace placeholders in title - if any key is missing, use a safe default
        try:
            for key, value in formatted_context.items():
                placeholder = "{" + key + "}"
                title = title.replace(placeholder, str(value))
                message = message.replace(placeholder, str(value))
            
            # Check if any placeholders remain unreplaced
            if '{' in title:
                # Use insight type as title if replacements failed
                title = template.get("title", insight_type.replace('_', ' ').title())
                # Remove unreplaced placeholders from title
                import re
                title = re.sub(r'\{[^}]+\}', '', title).strip()
            
            if '{' in message:
                # Remove unreplaced placeholders from message
                import re
                message = re.sub(r'\{[^}]+\}', '', message).strip()
        except Exception as e:
            logger.warning(f"Error replacing template variables: {e}")
        
        return {
            "title": title or "Financial Insight",
            "message": message or "Review your spending patterns to find opportunities for improvement."
        }
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Chat with tool calling support (for chatbot).
        
        Args:
            messages: Conversation history (role, content)
            tools: Available tools with schemas
            
        Returns:
            Dict with 'content' (str) and optional 'tool_calls' (list)
        """
        if not self.client:
            return {
                "content": "I'm sorry, I'm not configured to answer questions right now."
            }
        
        try:
            if self.provider == LLMProvider.GEMINI:
                return await self._chat_with_tools_gemini(messages, tools)
            else:
                # Fallback for non-Gemini providers
                logger.warning(f"Tool calling not implemented for {self.provider}")
                return {
                    "content": "I can only answer questions when using the Gemini model."
                }
        except Exception as e:
            logger.error(f"Chat with tools failed: {e}", exc_info=True)
            return {
                "content": f"I encountered an error: {str(e)}"
            }
    
    async def _chat_with_tools_gemini(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Chat with tools using Gemini."""
        import asyncio
        import json
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        import google.generativeai as genai
        
        # System instruction for the model
        system_instruction = """You are a helpful financial assistant. Your job is to help users understand and manage their finances using the available tools.

CRITICAL RULES:
1. ALWAYS call tools to get data before answering - NEVER respond without using at least one tool first
2. If you're not sure which tool to use, start with get_dashboard_summary to understand the user's situation
3. Use multiple tools if needed to give a complete answer
4. Be specific with numbers and dates from the actual data
5. Be conversational, friendly, and encouraging

TOOL MAPPING:
- "Where can I save money?" / "savings tips" / "reduce spending" → call list_insights with type='savings_opportunity'
- "How much did I spend?" → call get_spending_analytics or list_transactions
- "Show transactions" / "recent purchases" → call list_transactions
- "How are my goals?" / "goal progress" → call list_goals
- "Financial overview" / "how am I doing?" → call get_dashboard_summary
- "Spending trends" / "spending over time" → call get_spending_trends
- "What subscriptions do I have?" / "monthly subscriptions" / "recurring charges" → call list_subscriptions

NEVER say "I need more information" or "I don't have access" - you DO have access via tools. Use them!"""
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                gemini_messages.append({
                    "role": "user",
                    "parts": [content]
                })
            elif role == "assistant":
                gemini_messages.append({
                    "role": "model",
                    "parts": [content]
                })
            elif role == "function":
                # Function results go in user role with special formatting
                gemini_messages.append({
                    "role": "user",
                    "parts": [f"Tool '{msg['name']}' returned: {content}"]
                })
        
        # Convert tools to Gemini function declarations
        gemini_tools = []
        for tool in tools:
            gemini_tools.append(
                genai.protos.Tool(
                    function_declarations=[
                        genai.protos.FunctionDeclaration(
                            name=tool["name"],
                            description=tool["description"],
                            parameters=genai.protos.Schema(
                                type=genai.protos.Type.OBJECT,
                                properties={
                                    k: genai.protos.Schema(
                                        type=genai.protos.Type.STRING if v.get("type") == "string" else
                                        genai.protos.Type.INTEGER if v.get("type") == "integer" else
                                        genai.protos.Type.BOOLEAN if v.get("type") == "boolean" else
                                        genai.protos.Type.STRING,
                                        description=v.get("description", "")
                                    )
                                    for k, v in tool["parameters"].get("properties", {}).items()
                                },
                                required=tool["parameters"].get("required", [])
                            )
                        )
                    ]
                )
            )
        
        # Create a model with system instruction and tools
        model_with_tools = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_instruction,
            tools=gemini_tools,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 4096,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Generate response
        response = await asyncio.to_thread(
            model_with_tools.generate_content,
            gemini_messages
        )
        
        # Check for function calls
        if response.candidates and response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # Check if LLM wants to call a function
            if hasattr(part, 'function_call') and part.function_call:
                func_call = part.function_call
                
                # Convert arguments
                args = {}
                for key, value in func_call.args.items():
                    args[key] = value
                
                return {
                    "tool_calls": [{
                        "name": func_call.name,
                        "arguments": args
                    }]
                }
            
            # Regular text response
            if hasattr(part, 'text') and part.text:
                return {
                    "content": part.text.strip()
                }
        
        # Fallback
        return {
            "content": "I'm not sure how to respond to that."
        }


# Global instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
