# Using Google Gemini for AI Insights

The Smart Financial Coach now supports **three LLM providers** for generating AI-powered insights:

1. **OpenAI** (GPT-4, GPT-4o-mini)
2. **Anthropic** (Claude 3.5 Sonnet)
3. **Google Gemini** (Gemini 1.5 Flash/Pro)

## Configuration

### Option 1: Using Gemini

Add to your `.env` file:

```bash
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-1.5-flash  # Optional, defaults to gemini-1.5-flash
```

**To get a Google API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create or select a project
4. Copy your API key

### Option 2: Using OpenAI

```bash
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini
```

### Option 3: Using Anthropic

```bash
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Optional
```

## Provider Selection Priority

The system auto-detects which provider to use based on available API keys:

1. **OpenAI** (checked first)
2. **Anthropic** (checked second)
3. **Gemini** (checked third)
4. **Fallback templates** (if no API key is provided)

## Available Gemini Models

- `gemini-1.5-flash` - Fastest and most cost-effective (default)
- `gemini-1.5-pro` - Most capable, best quality
- `gemini-2.0-flash-exp` - Experimental multimodal model

## Testing Gemini Integration

1. **Add your API key to `.env`:**
   ```bash
   GOOGLE_API_KEY=AIza...
   ```

2. **Restart the server:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   /Users/pulkithooda/smart-fin-coach/backend/venv/bin/python /Users/pulkithooda/smart-fin-coach/backend/run.py > /tmp/server.log 2>&1 &
   ```

3. **Check the logs to confirm Gemini is being used:**
   ```bash
   grep "Gemini" /tmp/server.log
   # Should see: "Initialized Gemini client with model: gemini-1.5-flash"
   ```

4. **Generate insights:**
   ```bash
   TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"testuser4@fincoach.com","password":"SecurePass123!"}' | \
     grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
   
   curl -s -X POST "http://localhost:8000/api/v1/insights/generate" \
     -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
   ```

## Cost Comparison

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|----------|-------|----------------------|------------------------|
| **Gemini** | gemini-1.5-flash | $0.075 | $0.30 |
| **Gemini** | gemini-1.5-pro | $1.25 | $5.00 |
| **OpenAI** | gpt-4o-mini | $0.15 | $0.60 |
| **Anthropic** | claude-3-5-sonnet | $3.00 | $15.00 |

**Recommendation:** Use `gemini-1.5-flash` for production - it's the most cost-effective while still providing excellent quality.

## Switching Providers

To switch between providers, simply:

1. Comment out/remove the current API key
2. Add the new provider's API key
3. Restart the server

Example - switching from OpenAI to Gemini:

```bash
# .env file
# OPENAI_API_KEY=sk-...  # Comment out
GOOGLE_API_KEY=AIza...    # Add this
```

The system will automatically detect and use Gemini!

## Troubleshooting

**Issue:** "Failed to initialize Gemini client"
- **Solution:** Make sure `google-generativeai` package is installed: `pip install google-generativeai`

**Issue:** Invalid API key error
- **Solution:** Verify your API key is correct at [Google AI Studio](https://makersuite.google.com/app/apikey)

**Issue:** Rate limit errors
- **Solution:** Gemini has generous free tier limits. If exceeded, consider upgrading or switching models.

## Implementation Details

The Gemini integration includes:

- ✅ Auto-detection of Google API key
- ✅ Async execution support (using `asyncio.to_thread`)
- ✅ JSON response parsing with fallback
- ✅ Configurable model selection via `GEMINI_MODEL` env var
- ✅ Same prompt engineering as other providers
- ✅ Automatic fallback to template-based insights if API fails

All three providers use the same prompts and produce consistent insight quality!
