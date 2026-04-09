# 📚 Padhai AI — MP Board School Study Platform

AI-powered study platform for MP Board students (Class 6–12). Completely **free to run** using Google Gemini API + Streamlit Community Cloud.

**Features:** AI Tutor | MCQ Quiz | Study Notes | Important Questions  
**Languages:** Hindi + English Medium  
**Subjects:** All MP Board subjects, Class 6–12

---

## ⚡ Total Cost = ₹0

| Service | Free Limit | Cost |
|---------|-----------|------|
| Google Gemini API (`gemini-1.5-flash`) | 15 req/min, 10 lakh tokens/day | **FREE** |
| Streamlit Community Cloud (hosting) | Unlimited public apps | **FREE** |
| GitHub | Free for public repos | **FREE** |

---

## 🔑 Step 1 — Free API Key lena (Google Gemini)

1. **Google AI Studio** pe jao:
   `https://aistudio.google.com/app/apikey`

2. **Gmail account se login karo**

3. **"Create API Key"** button dabao

4. Key copy karo — aise dikhegi:
   `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

> Koi credit card nahi chahiye. No billing. Completely free.

---

## 🚀 Step 2 — Streamlit Community Cloud pe Deploy karna (Free Hosting)

### 2a. Streamlit Cloud pe account banao

1. `https://share.streamlit.io` pe jao
2. **"Sign in with GitHub"** — GitHub account se login karo

### 2b. App deploy karo

1. **"New app"** button dabao

2. Fill karo:
   ```
   Repository:  deependrakatiyar/road-safety-eda
   Branch:      main
   Main file:   app.py
   ```

3. **"Advanced settings"** → **"Secrets"** tab mein ye add karo:
   ```toml
   GEMINI_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXX"
   ```
   (Apni actual key se replace karo)

4. **"Deploy!"** dabao → 2-3 minute mein app live!

   URL milega: `https://yourname-padhai-ai.streamlit.app`

---

## 💻 Local Machine pe Run karna (Testing)

```bash
# 1. Clone karo
git clone https://github.com/deependrakatiyar/road-safety-eda.git
cd road-safety-eda

# 2. Install karo
pip install -r requirements.txt

# 3. API key set karo
# Windows:
set GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXX
# Mac / Linux:
export GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXX

# 4. Run karo
streamlit run app.py
```

Browser mein khulega: `http://localhost:8501`

---

## 🌐 Hostinger VPS pe Deploy karna (agar VPS hai)

> **Note:** Shared hosting pe ye kaam nahi karega (Python server nahi chalta).
> Sirf VPS / Cloud server pe chalega. Shared hosting hai to Step 2 (Streamlit Cloud) use karo.

```bash
# SSH karo
ssh root@your-vps-ip

# Python + pip install (agar nahi hai)
apt update && apt install python3 python3-pip screen -y

# Repo clone karo
git clone https://github.com/deependrakatiyar/road-safety-eda.git
cd road-safety-eda

# Dependencies install karo
pip3 install -r requirements.txt

# API key permanently set karo
echo 'export GEMINI_API_KEY="AIzaSyXXXXXXXXXX"' >> ~/.bashrc
source ~/.bashrc

# Background mein run karo (screen use karke)
screen -S padhai
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# Ctrl+A phir D — screen se bahar aao, app chalta rahega
```

Browser mein: `http://your-vps-ip:8501`

---

## ✅ Testing Checklist

App run hone ke baad ye test karo:

- [ ] Home page khulta hai
- [ ] Sidebar mein 4 pages dikh rahe hain (AI Tutor, Quiz, Notes, Important Questions)
- [ ] **AI Tutor** — sawal pucho, jawab aaye
- [ ] **Quiz** — Class 10 > Science > "Electricity" > 5 questions generate karo
- [ ] **Notes** — Class 10 > Science > "Electricity" > Summary Notes generate karo
- [ ] **Important Questions** — Class 10 > Science > "Electricity" > All Types
- [ ] Hindi medium select karo — Hindi mein jawab aaye

---

## ❓ Common Problems

| Problem | Solution |
|---------|----------|
| `GEMINI_API_KEY not found` | Key sahi se set karo, spelling check karo |
| `ResourceExhausted` error | Free limit (15 req/min) hit hui — 1 min wait karo |
| Quiz JSON error | Topic thoda alag likhke retry karo |
| Streamlit Cloud deploy fail | Secrets mein key add ki? Format: `GEMINI_API_KEY = "..."` |

---

## 📁 File Structure

```
padhai-ai/
├── app.py                          ← Home page
├── requirements.txt                ← Python dependencies
├── README.md                       ← Ye file (setup guide)
└── pages/
    ├── 1_AI_Tutor.py               ← Chat with AI tutor
    ├── 2_Quiz.py                   ← MCQ Practice
    ├── 3_Notes.py                  ← Study Notes generator
    └── 4_Important_Questions.py    ← Board exam questions
```

---

## 🆓 Gemini Free Tier Limits

| Limit | Value |
|-------|-------|
| Requests per minute | 15 |
| Tokens per day | 10,00,000 (1 Million) |
| Requests per day | 1,500 |

Ek student ke liye ye kaafi se zyada hai.
