# 🔐 AI Home Security System

A real-time AI-powered home security camera system that uses face recognition and an LLM-based interrogation flow to identify unknown visitors — with SMS alerts and a Flask web dashboard.

---

## 🚀 Features

- 🎥 **Live Camera Feed** — Real-time video capture via OpenCV
- 🧠 **Face Recognition** — DeepFace + Facenet matches faces against known household members
- 🕵️ **Unknown Person Interrogation** — Google Gemini AI generates and evaluates security questions
- 📲 **SMS Alerts** — Twilio sends instant alerts if an unknown person fails verification
- 🗃️ **Event Logging** — Flask + SQLAlchemy stores all Q&A sessions in a local SQLite database
- 👤 **Household Profiles** — JSON-based database of known members with room access and personal details

---

## 🗂️ Project Structure

```
ai-security/
├── app.py                  # Flask entry point, starts camera thread
├── camera_security.py      # Core logic: detection, recognition, AI interrogation
├── models.py               # SQLAlchemy database model
├── users.json              # Household member profiles
├── keys.py                 # API credentials (DO NOT COMMIT)
├── temp_face.jpg           # Temporary file used during face comparison

├── requirements.txt        # Python dependencies
├── .gitignore              # Excludes keys.py, DB files, etc.
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Activate — Windows:
venv\Scripts\activate

# Activate — Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, install manually and then generate one:

```bash
pip install opencv-python deepface mediapipe twilio google-generativeai flask flask-sqlalchemy
pip freeze > requirements.txt
```

### 4. Configure API Keys

Create a `keys.py` file in the project root:

```python
# keys.py
gemini_api_key = "YOUR_GEMINI_API_KEY"
account_sid    = "YOUR_TWILIO_ACCOUNT_SID"
auth_token     = "YOUR_TWILIO_AUTH_TOKEN"
twilio_number  = "+1XXXXXXXXXX"    # Your Twilio number
target         = "+91XXXXXXXXXX"   # Number to receive SMS alerts
```

> ⚠️ Never commit this file. Confirm `keys.py` is listed in `.gitignore` before pushing.

### 5. Add Training Images

Place one clear face photo per person inside a folder called `training images/`:

```
training images/
├── Alice.jpg
├── Bob.jpg
```

Update the path in `camera_security.py` if needed:

```python
known_faces_dir = "training images"
```

### 6. Update Household Data

Edit `users.json` to reflect your household members:

```json
[
  {
    "name": "Alice",
    "relation": "Daughter",
    "likes": ["cats", "piano"],
    "rooms_access": ["living room", "bedroom"]
  }
]
```

---

## ▶️ Running the App Locally

```bash
python app.py
```

Then open your browser and visit:

```
http://127.0.0.1:5000
```

The camera starts automatically. Press **Q** in the camera window to stop it.

---

## 📤 How to Put This on GitHub

### Step 1 — Create a `.gitignore` file

Create a file named `.gitignore` in your project root with this content:

```
keys.py
*.db
venv/
__pycache__/
temp_face.jpg
*.pyc
.env
training images/
```

> Training images contain real faces — keep them off public repositories.

### Step 2 — Initialize Git in Your Project Folder

Open a terminal inside your project folder and run:

```bash
git init
git add .
git commit -m "Initial commit"
```

### Step 3 — Create a New GitHub Repository

1. Go to [https://github.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Give it a name, e.g. `ai-home-security`
4. Set visibility to **Private** (recommended for a security project)
5. **Do not** check "Add a README" — you already have one
6. Click **"Create repository"**

### Step 4 — Connect and Push Your Code

GitHub will show you these commands after creating the repo — run them in your terminal:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-home-security.git
git branch -M main
git push -u origin main
```

### Step 5 — Verify

Open your GitHub repo in the browser and confirm:
- ✅ All your files are there
- ❌ `keys.py` is **not** listed anywhere

---

## 🔄 Pushing Future Changes

Whenever you make changes and want to update GitHub:

```bash
git add .
git commit -m "Brief description of what you changed"
git push
```

---

## 🛡️ Security Reminders

- Always keep `keys.py` out of GitHub via `.gitignore`
- Set your GitHub repo to **Private**
- If `keys.py` was ever accidentally pushed, rotate your Twilio and Gemini API keys immediately
- Review local privacy laws before deploying facial recognition software

---

## 📋 Requirements

- Python 3.8+
- A working webcam
- Twilio account with SMS capability enabled
- Google Gemini API key
- Windows / Mac / Linux

---

## 📄 License

MIT License
