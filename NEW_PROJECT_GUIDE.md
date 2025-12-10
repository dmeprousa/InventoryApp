# 🆕 DME INVENTORY MANAGEMENT - NEW PROJECT FROM SCRATCH

## 📁 **NEW PROJECT STRUCTURE**

```
Create NEW folder (separate from documentation):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp\
│
├── inventory_app.py           ⬅️ Main application
├── requirements.txt           ⬅️ Dependencies
├── .gitignore                 ⬅️ Git ignore file
├── README.md                  ⬅️ Documentation
│
├── oauth_credentials.json     ⬅️ Google OAuth (NEW - generate fresh)
└── token.json                 ⬅️ Auto-generated (don't create manually)

COMPLETELY SEPARATE from documentation project! ✅
```

---

## 🔑 **STEP 1: Get Google Credentials (NEW)**

### **A. Go to Google Cloud Console:**

```
https://console.cloud.google.com/
```

### **B. Create NEW Project:**

```
1. Click "Select a project" (top left)
2. Click "NEW PROJECT"
3. Project name: "DME Inventory System"
4. Click "CREATE"
5. Wait for project creation
6. Select the new project
```

### **C. Enable Google Sheets API:**

```
1. Go to: APIs & Services → Library
2. Search: "Google Sheets API"
3. Click on it
4. Click "ENABLE"
5. Wait for activation
```

### **D. Create OAuth Credentials:**

```
1. Go to: APIs & Services → Credentials
2. Click "CREATE CREDENTIALS"
3. Select "OAuth client ID"
4. If prompted:
   • Configure consent screen
   • User Type: External
   • App name: "DME Inventory App"
   • Support email: your email
   • Save
5. Back to create credentials:
   • Application type: "Desktop app"
   • Name: "Inventory Desktop Client"
   • Click "CREATE"
6. Download JSON file
7. Rename to: oauth_credentials.json
8. Save it
```

### **E. Get Gemini API Key:**

```
1. Go to: https://makersuite.google.com/app/apikey
   OR: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select your project (or create new)
4. Copy the API key
5. Save it somewhere (you'll need it)
```

---

## 📦 **STEP 2: Create Project Files**

### **Create the folder:**

```cmd
# Create new folder
mkdir D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp
cd D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp
```

### **Download these 4 files to the folder:**

```
1. inventory_app.py        (from Claude)
2. requirements.txt        (from Claude)
3. .gitignore             (from Claude)
4. README.md              (from Claude)
```

### **Add your credentials:**

```
5. oauth_credentials.json  (from Google Cloud Console)
```

**FINAL STRUCTURE:**
```
D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp\
├── inventory_app.py
├── requirements.txt
├── .gitignore
├── README.md
└── oauth_credentials.json ⬅️ YOUR FILE
```

---

## 💻 **STEP 3: Install Python (if needed)**

### **Check if Python installed:**

```cmd
python --version
```

**Should show:** `Python 3.x.x`

### **If not installed:**

```
1. Download: https://www.python.org/downloads/
2. Download latest (3.11 or 3.12)
3. Install with "Add to PATH" checked ✅
4. Restart computer
5. Test: python --version
```

---

## 📦 **STEP 4: Install Dependencies**

### **Open Command Prompt:**

```cmd
cd D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp
```

### **Create Virtual Environment (optional but recommended):**

```cmd
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate

# You'll see (venv) in prompt
```

### **Install packages:**

```cmd
pip install -r requirements.txt
```

### **If error, try:**

```cmd
pip install streamlit
pip install google-generativeai
pip install google-api-python-client
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install Pillow
pip install pandas
pip install openpyxl
```

---

## 🔧 **STEP 5: Configure App**

### **A. Add Gemini API Key:**

#### **Option 1: Environment Variable (Recommended)**

```cmd
# Windows Command Prompt
set GEMINI_API_KEY=your_api_key_here

# PowerShell
$env:GEMINI_API_KEY="your_api_key_here"
```

#### **Option 2: Streamlit Secrets**

Create file: `.streamlit/secrets.toml`

```toml
GEMINI_API_KEY = "your_api_key_here"
```

#### **Option 3: Direct in Code (Quick test only)**

Edit `inventory_app.py`, find line with `GEMINI_API_KEY` and add your key.

### **B. Set Google Sheet ID:**

In `inventory_app.py`, line ~26:

```python
SHEET_ID = "1R4uIReUPCe0RtO4NhVQqCgY_qb25LS1dfN9075xtcAg"
```

This is already your sheet! ✅

---

## ▶️ **STEP 6: First Run**

### **Start the app:**

```cmd
streamlit run inventory_app.py
```

### **First time authentication:**

```
1. Browser opens with Google login
2. Choose your Google account
3. Click "Allow" for permissions
4. App will create token.json
5. App starts!
```

---

## 🎯 **STEP 7: Test**

### **In the browser:**

```
1. Select Status: "In Stock"
2. Upload: Test photos (oxygen cylinders)
3. Click: "Extract Equipment Data"
4. Wait: AI processes
5. Review: Check extracted data
6. Edit: Fix if needed
7. Confirm: Each item
8. Add: Click "Add All to Inventory"
9. Success! Check Google Sheet
```

---

## ✅ **SUCCESS CHECKLIST**

```
Setup Complete:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ New folder created
□ 5 files in folder
□ oauth_credentials.json from Google
□ Dependencies installed
□ GEMINI_API_KEY configured
□ App starts without errors
□ Google authentication works
□ Can upload photos
□ Extraction works
□ Data added to Google Sheets

All ✅ → Perfect! 🎉
```

---

## 📋 **PROJECT INFO**

```
Project Name: DME Inventory Management
Location: D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp\
Type: Standalone Streamlit app
Purpose: Add equipment to Google Sheets from photos

Features:
✅ 23 categories
✅ 50+ item names
✅ AI extraction
✅ User confirmation
✅ Google Sheets integration
✅ Status tracking
✅ Duplicate detection

COMPLETELY INDEPENDENT! ✅
```

---

## 🔧 **DAILY USAGE**

### **Start app:**

```cmd
cd D:\Mine\Jobs\UpWork\dmeprousa\InventoryApp
streamlit run inventory_app.py
```

### **Stop app:**

```
Ctrl + C
```

### **Update app:**

```
1. Download new inventory_app.py
2. Replace old file
3. Restart app
```

---

## 📊 **GOOGLE SHEET**

```
Your Sheet:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: Dme Pro Inventory System
ID: 1R4uIReUPCe0RtO4NhVQqCgY_qb25LS1dfN9075xtcAg
URL: https://docs.google.com/spreadsheets/d/1R4uIReUPCe0RtO4NhVQqCgY_qb25LS1dfN9075xtcAg/edit

The app adds rows automatically! ✅
```

---

## 🚀 **DEPLOYMENT (OPTIONAL)**

### **Local Use:**

```
✅ Run on your computer
✅ Access: http://localhost:8501
✅ Fast and reliable
✅ No internet dependency (once set up)
```

### **Cloud Deployment (Later):**

```
1. Push to GitHub
2. Deploy on Streamlit Cloud
3. Share link with team
4. Access from anywhere

(But start with local first!)
```

---

## 🎉 **COMPLETE NEW PROJECT!**

```
╔═══════════════════════════════════════════════╗
║                                               ║
║  NEW PROJECT FROM SCRATCH                    ║
║                                               ║
║  Folder: InventoryApp\                       ║
║  Files: 5 (all new)                          ║
║  Credentials: Fresh from Google              ║
║  Dependencies: Install fresh                 ║
║  Configuration: Set up new                   ║
║                                               ║
║  COMPLETELY INDEPENDENT! ✅                  ║
║                                               ║
║  No relation to documentation project! ✅    ║
║                                               ║
╚═══════════════════════════════════════════════╝
```

---

**Next: Download the 4 files I'll create! 📦**
