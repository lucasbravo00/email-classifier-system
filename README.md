# Email Classification System — Projector Help Center

Automatic system for classifying incoming support emails and generating ready-to-review response drafts.

---

## How it works

When an email arrives, the system:
1. Reads it from your Outlook inbox (or you paste it manually)
2. Classifies it using a Machine Learning model (Naive Bayes + TF-IDF)
3. Selects the best matching response from your predefined responses database
4. Generates a draft and saves it to your Outlook Drafts folder
5. **Nothing is sent automatically** — every draft requires human review before sending

The model learns from example emails (`training_emails.json`) and maps each one to a response ID from your responses database (`responses.json`). Keywords in the response file are used to explain predictions, but classification is done entirely by the ML model based on patterns learned during training.

---

## Project structure

```
email-classifier-system/
├── config.json                  # Your configuration (not uploaded to GitHub)
├── config.example.json          # Template — copy this to create config.json
├── main.py                      # Main entry point (interactive mode)
├── auto_runner.py               # Background mode (checks email every N minutes)
├── requirements.txt             # Python dependencies
├── src/
│   ├── 01_data_manager.py       # Loads and manages responses.json
│   ├── 02_text_preprocessor.py  # Cleans and tokenizes email text
│   ├── 03_model_trainer.py      # Trains and saves the ML model
│   ├── 04_classifier.py         # Classifies emails using the trained model
│   ├── 05_draft_generator.py    # Builds the response draft
│   ├── 06_interface.py          # Interactive terminal interface
│   └── 07_outlook_connector.py  # Reads inbox and saves drafts via Microsoft Graph API
└── data/
    ├── responses.json           # Your predefined responses (not uploaded to GitHub)
    ├── training_emails.json     # Training examples (not uploaded to GitHub)
    └── trained_model.pkl        # Saved model — auto-generated after training
```

---

## Setup

### Step 1 — Install dependencies

```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Or run the included script:
```bash
bash install_dependencies.sh
```

### Step 2 — Create your config file

Copy the example config and fill in your values:

```bash
cp config.example.json config.json
```

The file looks like this:

```json
{
  "responses_path": "data/responses.json",
  "training_emails_path": "data/training_emails.json",
  "model_path": "data/trained_model.pkl",
  "confidence_threshold": 0.60,
  "language": "english",
  "outlook": {
    "client_id": "YOUR_AZURE_CLIENT_ID_HERE",
    "tenant_id": "consumers"
  }
}
```

`confidence_threshold` controls the minimum confidence required for the model to use a prediction automatically. Below this threshold, the email is flagged for manual review.

### Step 3 — Prepare your data files

You need two files inside the `data/` folder before training:

**`data/responses.json`** — your predefined responses. Each response requires `id`, `title`, `category`, and `body`:

```json
[
  {
    "id": 170,
    "title": "Getting Started",
    "category": "Onboarding",
    "body": "Welcome! To get started, go to projectorstream.com and click Sign Up..."
  },
  {
    "id": 130,
    "title": "Video Streaming Standards",
    "category": "Video Quality",
    "body": "To ensure best performance, please review our video format guide at..."
  }
]
```

**`data/training_emails.json`** — example emails for each response. The more examples per response, the more accurate the model:

```json
[
  {"text": "I just signed up and have no idea where to begin, can you help?", "label": "170"},
  {"text": "How do I get started with Projector?", "label": "170"},
  {"text": "My video keeps buffering, what format should I use?", "label": "130"}
]
```

Each `label` must match the `id` of a response in `responses.json`.

### Step 4 — Connect to Outlook (optional but recommended)

Without Outlook connected, the system works in manual mode — you paste emails directly into the terminal.

To enable Outlook integration:

1. Go to [portal.azure.com](https://portal.azure.com) and sign in with your Microsoft account (free)
2. Go to **Azure Active Directory → App registrations → New registration**
3. Name it anything (e.g. `email-classifier`), leave everything else as default, click **Register**
4. Copy the **Application (client) ID** shown on the overview page
5. Go to **API permissions → Add a permission → Microsoft Graph → Delegated permissions**
6. Add: `Mail.Read` and `Mail.ReadWrite`
7. Click **Grant admin consent**
8. Paste the client ID into your `config.json`:

```json
"outlook": {
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant_id": "consumers"
}
```

### Step 5 — Train the model

```bash
python main.py --train-only
```

This reads `training_emails.json`, trains the model, and saves it to `data/trained_model.pkl`. You only need to retrain when you add new responses or new training examples.

To force retraining even if a saved model already exists:

```bash
python main.py --retrain
```

---

## Running the system

### Interactive mode (manual)

Process one email at a time from the terminal:

```bash
python main.py
```

On first run with Outlook configured, a browser window will open asking you to log in with your Microsoft account. After that, the token is cached locally and you won't be asked again.

### Automatic mode (background)

Checks your inbox every 10 minutes and processes new emails automatically:

```bash
python auto_runner.py
```

Custom interval:

```bash
python auto_runner.py --interval 5    # every 5 minutes
python auto_runner.py --once          # run once and exit (useful for testing)
```

Use the helper scripts to start and stop it as a background process:

```bash
bash start_auto_runner.sh
bash stop_auto_runner.sh
```

Logs are saved to `data/auto_runner.log`.

---

## How the model classifies emails

The system uses a **TF-IDF + Naive Bayes** pipeline from scikit-learn:

- **TF-IDF** converts email text into a numerical vector, weighing words that appear frequently in one category but rarely in others
- **Naive Bayes** uses those vectors to predict which response ID best matches the email
- Confidence is calculated from the prediction probability. Emails below the `confidence_threshold` are flagged for manual review instead of auto-drafted

The `keywords` field in responses (if present) is used only to explain predictions — it does not affect how the model classifies emails.

---

## Adding new responses

1. Add the new response to `data/responses.json` with a unique `id`
2. Add at least 5–10 example emails to `data/training_emails.json` with that `id` as the label
3. Retrain: `python main.py --retrain`

The more training examples you provide per response, the more accurately the model will classify them.

---

## Notes

- Requires Python 3.8+
- Designed for up to ~50 predefined responses
- Training takes under 5 seconds with the current dataset
- The model file (`trained_model.pkl`) is excluded from the repository — each user trains their own model locally
- `config.json` and all files in `data/` (except `.gitkeep`) are excluded from the repository for privacy

---

## License

Internal — Projector Help Center
