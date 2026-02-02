# 🧠 Psychometric User Manual — Streamlit App

A bilingual (EN/DE) psychometric assessment tool with AI-powered deep analysis.

---

## 🚀 DEPLOYMENT GUIDE (Step by Step)

### Step 1: Get your files ready

You need these files (they're all in this folder):
```
├── app.py                          ← The app
├── requirements.txt                ← Dependencies  
├── .gitignore                      ← Keeps secrets safe
├── .streamlit/
│   ├── config.toml                 ← Theme settings
│   └── secrets.toml.example        ← Template for your API key
└── README.md                       ← This file
```

### Step 2: Create a GitHub repository

1. Go to **github.com** → click **+** (top right) → **New repository**
2. Name it: `psychometric-assessment` (or whatever you want)
3. Set it to **Public** (Streamlit Cloud free tier requires public repos)
4. **Do NOT** check "Add a README file" (we already have one)
5. Click **Create repository**
6. You'll see instructions for uploading — follow "upload an existing file" or use the steps below

### Step 3: Upload files to GitHub

**Option A — Upload via browser (easiest):**
1. On your new repo page, click **"uploading an existing file"**
2. Drag ALL files from this folder into the upload area
3. ⚠️ **IMPORTANT:** Also drag the `.streamlit` folder (with config.toml inside)
4. ⚠️ **Do NOT upload** `secrets.toml.example` — it's just a template
5. Click **"Commit changes"**

**Option B — Upload via command line:**
```bash
cd /path/to/this/folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/psychometric-assessment.git
git push -u origin main
```

### Step 4: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your **GitHub account**
3. Click **"New app"**
4. Select:
   - **Repository:** `YOUR_USERNAME/psychometric-assessment`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy!"**

### Step 5: Add your Gemini API key

1. Your app will try to start but fail (no API key yet) — that's fine
2. In Streamlit Cloud, click **"Settings"** (⚙️ gear icon on your app)
3. Go to the **"Secrets"** tab
4. Paste this:
```toml
GEMINI_API_KEY = "your-actual-gemini-api-key-here"
```
5. Click **Save**
6. Your app will automatically restart

### Step 6: Done! 🎉

Your app is now live at: `https://YOUR_USERNAME-psychometric-assessment-app-XXXX.streamlit.app`

Share this URL with anyone. They can:
- Take the 43-question assessment
- See their visual summary with trait bars
- Generate an AI-powered deep analysis
- Download results as .md or .html (print to PDF)

---

## 💡 TIPS

- **Custom domain:** In Streamlit settings → "Custom subdomain" → pick a nicer URL
- **Private repo:** Requires Streamlit Teams (paid). Free tier = public repo only
- **Cost:** Completely free. Gemini 2.5 Flash free tier allows ~1000 profiles/day
- **To update:** Just push new code to GitHub → Streamlit auto-deploys

---

## 🔧 LOCAL TESTING

To run locally before deploying:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml and paste your real API key

# 3. Run
streamlit run app.py
```

Opens at http://localhost:8501

---

## 📊 HOW IT WORKS

- **43 questions** across 3 phases (Discovery, Stress Testing, Solution Design)
- **Forced-choice + intensity** (pick A or B, then rate: slightly/clearly/strongly)
- **13 trait scores** computed from primary + secondary question loading
- **AI deep analysis** via Gemini 2.5 Flash (10 chapters, ~3000 words)
- **No database needed** — everything runs in the user's browser session
- **No user data stored** — answers exist only during the session
