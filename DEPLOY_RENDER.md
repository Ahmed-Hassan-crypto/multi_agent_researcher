# Deploy to Render (Free)

## Option 1: From GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Deploy to Render"
   # Create repo on GitHub and push
   ```

2. **Deploy**
   - Go to https://dashboard.render.com
   - Sign up with GitHub
   - Click "New" → "Web Service"
   - Select your repo
   - Configure:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `streamlit run app.py --server.address 0.0.0.0`
   - Add Environment Variables:
     - `TAVILY_API_KEY` = your Tavily key
     - `GROQ_API_KEY` = your Groq key
     - `USE_GROQ` = true
   - Click "Deploy"

**Your app will be live at:** `https://your-app-name.onrender.com`

---

## Option 2: From render.yaml

1. Push code to GitHub
2. Go to https://dashboard.render.com
3. Click "New" → "Blueprint"
4. Connect your GitHub repo
5. Select `render.yaml` file
6. Add secrets in the form:
   - `TAVILY_API_KEY`
   - `GROQ_API_KEY`
7. Click "Apply"

---

## Get Free API Keys

| Service | Link |
|---------|------|
| **Tavily** (Search) | https://tavily.com |
| **Groq** (LLM) | https://console.groq.com |

---

## Troubleshooting

**Build failing?**
- Make sure requirements.txt is in root directory
- Check Python version (3.11)

**App not loading?**
- Verify API keys are set in Render dashboard
- Check logs in "Logs" tab

**Slow response?**
- Groq free tier has rate limits
- Consider upgrading for production