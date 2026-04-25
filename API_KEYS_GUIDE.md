# API Keys Setup Guide

Your LLM Council now supports **3 providers** with different models!

## Current Configuration

### Council Members (in `backend/config.py`):
1. **GPT-3.5-turbo** (OpenAI) - Fast and cheap
2. **Gemini-1.5-flash** (Google) - Free tier available  
3. **Llama-3.1-70b** (Groq) - Completely free
4. **Mixtral-8x7b** (Groq) - Completely free

### Chairman Model:
- **Gemini-1.5-pro** (Google) - Best free model for synthesis

---

## 🔑 Getting API Keys

### 1. Groq (100% FREE) ✅ Already Set
- ✓ You already have this configured
- Free tier: **14,400 requests/day**
- No credit card required

### 2. Google Gemini (FREE Tier)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

**Free Tier Limits:**
- 15 requests per minute
- 1500 requests per day
- No credit card required!

### 3. OpenAI (Pay-as-you-go)
1. Go to: https://platform.openai.com/api-keys
2. Sign up/sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Add to `.env`: `OPENAI_API_KEY=your_key_here`
6. Add $5-10 credits to your account

**Pricing:**
- GPT-3.5-turbo: ~$0.50 per 1M tokens (very cheap!)
- GPT-4: ~$10-30 per 1M tokens (expensive)

---

## 🧪 Testing Your Setup

Run the test script to verify all providers:

```powershell
python test_providers.py
```

This will:
- Check which API keys are configured
- Test each provider with a simple query
- Show you which ones are working

---

## 💡 Recommended Setup

### Option 1: Maximum Diversity (Recommended)
Use what's configured - mix of all three providers for best results!

### Option 2: 100% Free
If you don't want to pay, use only **Groq + Google**:

```python
COUNCIL_MODELS = [
    "gemini-1.5-flash",           # Google (free)
    "llama-3.1-70b-versatile",    # Groq (free)
    "mixtral-8x7b-32768",         # Groq (free)
    "llama-3.1-8b-instant",       # Groq (free)
]

CHAIRMAN_MODEL = "gemini-1.5-pro"  # Google (free)
```

### Option 3: Best Quality (Costs Money)
For maximum intelligence:

```python
COUNCIL_MODELS = [
    "gpt-4",                      # OpenAI (expensive but smart)
    "gpt-3.5-turbo",              # OpenAI (cheap and fast)
    "gemini-1.5-pro",             # Google (free, very good)
    "llama-3.1-70b-versatile",    # Groq (free, decent)
]

CHAIRMAN_MODEL = "gpt-4"  # Best synthesis
```

---

## 🔧 Configuration Files

Edit these files to change models:

### `backend/config.py`
Contains the list of council models and chairman model

### `.env`
Contains your API keys (don't commit this to git!)

---

## 📊 Model Comparison

| Provider | Model | Cost | Intelligence | Speed |
|----------|-------|------|--------------|-------|
| Groq | llama-3.1-70b | FREE | ⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| Groq | mixtral-8x7b | FREE | ⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| Groq | llama-3.1-8b | FREE | ⭐⭐ | ⚡⚡⚡⚡⚡ |
| Google | gemini-1.5-pro | FREE* | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| Google | gemini-1.5-flash | FREE* | ⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| OpenAI | gpt-4 | $$$$ | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| OpenAI | gpt-3.5-turbo | $ | ⭐⭐⭐ | ⚡⚡⚡⚡ |

*FREE within rate limits (15 RPM for Google)

---

## 🚀 Next Steps

1. Get your Google API key (it's free!)
2. Run `python test_providers.py` to verify
3. Start the app: `.\start.ps1`
4. Ask the council questions and see the diversity!

---

## ⚠️ Troubleshooting

**"HTTP 401 Unauthorized"**
- Check your API key is correct in `.env`
- Make sure there are no extra spaces

**"HTTP 429 Too Many Requests"**
- You hit rate limits
- Wait a minute and try again
- Use fewer requests or upgrade tier

**"Model not found"**
- Check model name spelling in config.py
- Verify the model exists for that provider

**"No response returned"**
- Check your internet connection
- Verify API key has credits (for OpenAI)
- Check provider status pages
