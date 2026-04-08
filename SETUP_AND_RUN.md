# 🚀 How to Run the System on Your Mac

## Step 1 — Install dependencies (only once)

Open Terminal, go to the project folder and run:

```bash
cd ~/Documents/email-classifier-system
bash install_dependencies.sh
```

---

## Step 2 — Run without Outlook (manual mode, test first)

This lets you paste emails manually to verify everything works:

```bash
python main.py
```

You'll see:
```
🔧 Initializing system...
🎓 Training model from scratch...
✅ System ready!

📧 Email Classifier - Help Center
────────────────────────────────────────
What would you like to do?
  1. Fetch unread emails from Outlook
  2. Paste an email manually
  3. Exit
```

Choose option **2**, paste a test email, and the system will:
- Classify it automatically
- Show you the suggested response with confidence score
- Generate a full draft ready to send
- Ask if you want to save it

---

## Step 3 — Connect to your Outlook (personal account)

### 3.1 Register the app on Azure (free, ~10 minutes)

1. Go to https://portal.azure.com and sign in with your Microsoft account
2. Search for **"App registrations"** → click **"New registration"**
3. Name: `EmailClassifier` (or anything you like)
4. Supported account types: **Personal Microsoft accounts only**
5. Click **Register**
6. Copy the **Application (client) ID** — you'll need it in step 3.2

### 3.2 Add permissions

In your new app page:
1. Click **"API permissions"** → **"Add a permission"**
2. Choose **Microsoft Graph** → **Delegated permissions**
3. Search and add: `Mail.Read`, `Mail.ReadWrite`
4. Click **"Grant admin consent"** if available

### 3.3 Add your Client ID to config.json

Open `config.json` and replace `YOUR_CLIENT_ID_HERE` with the ID you copied:

```json
{
  "outlook": {
    "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "tenant_id": "consumers"
  }
}
```

### 3.4 Run the system

```bash
python main.py
```

On first run it will open your browser to log into your Microsoft account.
After that, your token is saved locally and you won't need to log in again.

---

## Other useful commands

```bash
# Force retrain the model (e.g. after adding new responses)
python main.py --retrain

# Train only (no interface)
python main.py --train-only

# Run tests
python test_model_trainer.py
```

---

## Project structure

```
email-classifier-system/
├── main.py                      ← Run this
├── config.json                  ← Your settings and Outlook credentials
├── install_dependencies.sh      ← Run once to install packages
├── src/
│   ├── 01_data_manager.py       ✅ Loads responses
│   ├── 02_text_preprocessor.py  ✅ Cleans email text
│   ├── 03_model_trainer.py      ✅ Trains ML model
│   ├── 04_classifier.py         ✅ Classifies emails
│   ├── 05_draft_generator.py    ✅ Creates response drafts
│   ├── 06_interface.py          ✅ User interface
│   └── 07_outlook_connector.py  ✅ Reads/writes Outlook emails
└── data/
    ├── responses.json            ← Your predefined responses
    ├── training_emails.json      ← Training examples (24 emails)
    └── trained_model.pkl         ← Saved model (created on first run)
```
