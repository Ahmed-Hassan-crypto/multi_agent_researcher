# Deploy for Free - Local LLM Edition

## ⚠️ Important: Local LLMs Can't Be Deployed to Free Cloud Platforms

**Problem:** Free platforms (Streamlit Cloud, Hugging Face) cannot access your local Ollama server. They don't have access to your machine!

**Solution:** Use **Groq** (free cloud LLM) instead of Ollama for deployment.

---

## Option 1: Deploy with Groq (Free Cloud - RECOMMENDED)

### Step 1: Get Free Groq API Key
1. Go to https://console.groq.com
2. Create account → API Keys
3. Copy your API key (free 60k tokens/min!)

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "Update for Groq deployment"
# Create repo on GitHub and push
```

### Step 3: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Select your repo
4. **Secrets** (Advanced settings):
   ```
   TAVILY_API_KEY=your_tavily_key
   GROQ_API_KEY=your_groq_key
   USE_GROQ=true
   ```
5. Deploy!

**Live at:** `https://your-app-name.streamlit.app`

---

## Option 2: Local Use Only (Not Shareable)

If you only want to use locally (not deploy):

```bash
# Install Ollama from https://ollama.com
ollama pull qwen3.5:4b
ollama serve

# In another terminal:
cd multi_agent_researcher
pip install -r requirements.txt
streamlit run app.py
```

---

## Option 3: Self-Hosted Server (Paid AWS/VPS)

If you want a personal server others can access:

1. **Rent a VPS** (~$5/month): Hetzner, DigitalOcean, Linode
2. Install Ollama on it
3. Set `OLLAMA_BASE_URL=http://your-server-ip:11434`
4. Deploy Streamlit to the same server

---

## Quick Comparison

| Option | Free? | Shareable? | Speed |
|--------|-------|------------|-------|
| Groq + Streamlit Cloud | ✅ Yes | ✅ Yes | Fast |
| Ollama + Local | ✅ Yes | ❌ No | Depends on PC |
| VPS + Ollama | ❌ $5/mo | ✅ Yes | Depends on VPS |

**Recommendation:** Use **Option 1 (Groq)** - fastest path to a live, shareable demo!