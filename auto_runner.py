"""
Auto Runner: Automatic email processing loop
Runs in the background, checks for new emails every N minutes,
classifies them and saves drafts automatically.

Usage:
  python auto_runner.py              → Runs every 10 minutes (default)
  python auto_runner.py --interval 5 → Runs every 5 minutes
  python auto_runner.py --once       → Runs once and exits (useful for testing)
"""

import json
import os
import re
import sys
import time
import importlib.util
from datetime import datetime


# ─── DYNAMIC MODULE LOADER ─────────────────────────────────────────────────────

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─── CONFIG ────────────────────────────────────────────────────────────────────

def load_config(path: str = "config.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


# ─── LOGGING ───────────────────────────────────────────────────────────────────

LOG_PATH = "data/auto_runner.log"
PROCESSED_IDS_PATH = "data/processed_email_ids.json"

def log(message: str):
    """Write a timestamped message to the log file and print to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─── PROCESSED EMAIL ID TRACKING ───────────────────────────────────────────────

def load_processed_ids() -> set:
    """Load the set of email IDs that have already been drafted."""
    if os.path.exists(PROCESSED_IDS_PATH):
        with open(PROCESSED_IDS_PATH, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(ids: set):
    """Persist the set of processed email IDs to disk."""
    os.makedirs("data", exist_ok=True)
    with open(PROCESSED_IDS_PATH, "w") as f:
        json.dump(list(ids), f)


# ─── THREAD BODY EXTRACTOR ─────────────────────────────────────────────────────

# Patterns that mark the start of quoted/previous messages in email threads
# Note: no ^ anchor so they match anywhere in the text, not just line starts
THREAD_SEPARATORS = [
    r"From:.*@",
    r"On .{10,100} wrote:",
    r"_{5,}",
    r"-{5,}Original Message-{5,}",
    r"Sent from my ",
    r"El .{5,80} escribió:",          # Spanish Outlook threads
    r"Le .{5,80} a écrit :",          # French
]
THREAD_PATTERN = re.compile(
    "|".join(THREAD_SEPARATORS),
    re.IGNORECASE
)

def extract_latest_message(body: str) -> str:
    """
    Extract only the latest/newest message from an email thread body,
    stripping out all quoted history below it.
    Works with both plain text and HTML emails.
    """
    # Strip HTML tags if body is HTML
    if "<html" in body.lower() or "<div" in body.lower():
        # Remove blockquote sections (quoted history in HTML emails)
        body = re.sub(r"<blockquote[^>]*>.*?</blockquote>", "", body, flags=re.DOTALL | re.IGNORECASE)
        # Remove all remaining HTML tags
        body = re.sub(r"<[^>]+>", " ", body)
        # Decode common HTML entities
        body = body.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    # Collapse whitespace
    body = re.sub(r"\r\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)

    # Find the first line that looks like a thread separator
    match = THREAD_PATTERN.search(body)
    if match:
        # Keep only everything above the separator
        body = body[:match.start()].strip()

    return body.strip()


# ─── WPFORM PARSER ─────────────────────────────────────────────────────────────

def parse_wpform(body: str) -> dict | None:
    """
    Detect if an email is a WPForms submission and extract its fields.
    WPForms emails are HTML tables where each field label (<b>Label</b>)
    is followed by the value in the next table cell.
    Returns a dict with 'name', 'email', 'message' if it's a WPForm,
    or None if it's a regular email.
    """
    # WPForms emails always contain this label
    if "Comment or Message" not in body:
        return None

    # Extract all cell text values in order from the HTML table
    # Each label (<b>text</b>) is followed by the value in the next <td>
    cells = re.findall(r"<td[^>]*>.*?</td>", body, re.DOTALL | re.IGNORECASE)

    def cell_text(cell):
        """Strip all HTML tags from a cell and clean whitespace."""
        text = re.sub(r"<[^>]+>", "", cell)
        text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        return " ".join(text.split()).strip()

    # Build a label→value map by pairing bold labels with the next cell's value
    fields = {}
    i = 0
    while i < len(cells):
        text = cell_text(cells[i])
        if text in ("Name", "Email", "Comment or Message"):
            # Value is in the next cell
            if i + 1 < len(cells):
                fields[text] = cell_text(cells[i + 1])
                i += 2
                continue
        i += 1

    return {
        "name":    fields.get("Name", ""),
        "email":   fields.get("Email", ""),
        "message": fields.get("Comment or Message", ""),
    }


# ─── CORE PROCESSING ───────────────────────────────────────────────────────────

def process_emails(outlook, classifier, draft_generator, confidence_threshold: float):
    """
    Fetch unread emails, classify each one, and:
    - If already processed (ID in local file): skip silently
    - If confidence >= threshold: save draft + record ID locally (leave unread in Outlook)
    - If confidence <  threshold: do nothing (leave unread for manual review)

    Returns:
        (processed, skipped) — counts of emails handled
    """
    emails = outlook.get_unread_emails(max_count=20)

    if not emails:
        log("📭 No unread emails found.")
        return 0, 0

    processed_ids = load_processed_ids()
    new_emails = [e for e in emails if e.get("id") not in processed_ids]

    already_done = len(emails) - len(new_emails)
    if already_done > 0:
        log(f"📬 Found {len(emails)} unread email(s) — {already_done} already drafted, {len(new_emails)} new.")
    else:
        log(f"📬 Found {len(new_emails)} new unread email(s). Processing...")

    if not new_emails:
        return 0, 0

    processed = 0
    skipped = 0

    for email in new_emails:
        sender   = email.get("sender", "")
        subject  = email.get("subject", "")
        body     = email.get("body", "")
        email_id = email.get("id", "")

        log(f"  → [{sender}] {subject}")

        # Check for WPForm — only if sent directly from the WPForms server
        is_wpform_sender = "no-reply@projector.help" in sender.lower()
        wpform = parse_wpform(body) if is_wpform_sender else None
        if wpform and wpform["message"]:
            log(f"     📋 WPForm detected — Name: {wpform['name']}, Email: {wpform['email']}")
            classify_body = wpform["message"]
            # Override email fields so the draft goes to the real person
            email = dict(email)
            email["sender"]      = wpform["email"]
            email["sender_name"] = wpform["name"]
        else:
            # Regular email — extract only the latest message from the thread
            classify_body = extract_latest_message(body)

        # Classify using only the body — subject is too unpredictable and can mislead the model
        result = classifier.classify_email("", classify_body)
        confidence = result.get("confidence", 0)
        response_id = result.get("response_id")

        if confidence >= confidence_threshold and response_id:
            # High confidence — generate draft, save to Outlook, record ID locally
            log(f"     ✅ Classified as #{response_id} with {confidence*100:.1f}% confidence")

            draft = draft_generator.generate_draft(
                original_email=email,
                response_id=response_id
            )

            saved = outlook.save_as_draft(draft)

            if saved:
                # Record locally so we don't draft it again — but leave unread in Outlook
                processed_ids.add(email_id)
                save_processed_ids(processed_ids)
                log(f"     📝 Draft saved. Email left unread in Outlook for tracking.")
                processed += 1
            else:
                log(f"     ❌ Failed to save draft. Will retry next cycle.")
                skipped += 1

        else:
            # Low confidence — leave untouched for manual review
            log(f"     ⚠️  Low confidence ({confidence*100:.1f}%) — skipped, left unread for manual review.")
            skipped += 1

    return processed, skipped


# ─── MAIN LOOP ─────────────────────────────────────────────────────────────────

def main():
    # Parse arguments
    interval_minutes = 10
    run_once = "--once" in sys.argv

    if "--interval" in sys.argv:
        idx = sys.argv.index("--interval")
        try:
            interval_minutes = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("⚠️  Invalid --interval value. Using default: 10 minutes.")

    config = load_config()

    # ── Load modules
    dm_mod = load_module("data_manager",      "src/01_data_manager.py")
    tp_mod = load_module("text_preprocessor", "src/02_text_preprocessor.py")
    mt_mod = load_module("model_trainer",     "src/03_model_trainer.py")
    cl_mod = load_module("classifier",        "src/04_classifier.py")
    dg_mod = load_module("draft_generator",   "src/05_draft_generator.py")
    oc_mod = load_module("outlook_connector", "src/07_outlook_connector.py")

    # ── Initialize components
    data_manager      = dm_mod.DataManager(config["responses_path"])
    text_preprocessor = tp_mod.TextPreprocessor()
    model_trainer     = mt_mod.ModelTrainer()
    draft_generator   = dg_mod.DraftGenerator(
        data_manager,
        signature="Best regards,\nThe Projector Support Team"
    )

    data_manager.load_responses()

    # ── Load trained model
    model_path = config["model_path"]
    if not os.path.exists(model_path):
        print("❌ No trained model found. Run 'python main.py --train-only' first.")
        sys.exit(1)

    model_trainer.load_model(model_path)

    # ── Connect to Outlook
    outlook_cfg = config.get("outlook", {})
    client_id   = outlook_cfg.get("client_id", "")

    if not client_id or client_id == "YOUR_CLIENT_ID_HERE":
        print("❌ Outlook not configured. Add your CLIENT_ID to config.json.")
        sys.exit(1)

    print("\n🔐 Connecting to Outlook...")
    outlook = oc_mod.OutlookConnector(
        client_id=client_id,
        tenant_id=outlook_cfg.get("tenant_id", "consumers"),
        token_cache_path="data/token_cache.json"
    )

    if not outlook.authenticate():
        print("❌ Outlook authentication failed. Exiting.")
        sys.exit(1)

    # ── Initialize classifier
    classifier = cl_mod.EmailClassifier(model_trainer, text_preprocessor, data_manager)
    confidence_threshold = config.get("confidence_threshold", 0.7)

    # ── Start loop
    if run_once:
        log("🚀 Running once...")
        processed, skipped = process_emails(outlook, classifier, draft_generator, confidence_threshold)
        log(f"✅ Done. Processed: {processed} | Skipped (low confidence): {skipped}")
    else:
        log(f"🚀 Auto runner started. Checking every {interval_minutes} minute(s). Press Ctrl+C to stop.")
        log(f"   Confidence threshold: {confidence_threshold*100:.0f}%")
        log(f"   Log file: {LOG_PATH}")

        while True:
            log(f"🔄 Checking inbox...")
            try:
                processed, skipped = process_emails(outlook, classifier, draft_generator, confidence_threshold)
                log(f"   ✅ Done. Drafts saved: {processed} | Left for manual review: {skipped}")
            except Exception as e:
                log(f"   ❌ Error during processing: {e}")

            log(f"   💤 Sleeping {interval_minutes} minute(s)...\n")
            time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    main()
