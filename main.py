"""
Main: Entry point for the Email Classification System
Usage:
  python main.py               → Run the full system (train + launch interface)
  python main.py --train-only  → Train and save the model, then exit
"""

import json
import os
import sys
import importlib.util


# ─── DYNAMIC MODULE LOADER ─────────────────────────────────────────────────────
# Python doesn't allow importing modules whose names start with a number,
# so we use importlib to load them dynamically.

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─── CONFIG ────────────────────────────────────────────────────────────────────

def load_config(path: str = "config.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    config = load_config()

    # ── Load all modules
    dm_mod  = load_module("data_manager",       "src/01_data_manager.py")
    tp_mod  = load_module("text_preprocessor",  "src/02_text_preprocessor.py")
    mt_mod  = load_module("model_trainer",      "src/03_model_trainer.py")
    cl_mod  = load_module("classifier",         "src/04_classifier.py")
    dg_mod  = load_module("draft_generator",    "src/05_draft_generator.py")
    ui_mod  = load_module("interface",          "src/06_interface.py")
    oc_mod  = load_module("outlook_connector",  "src/07_outlook_connector.py")

    # ── Initialize core components
    print("\n🔧 Initializing system...")

    data_manager       = dm_mod.DataManager(config["responses_path"])
    text_preprocessor  = tp_mod.TextPreprocessor()
    model_trainer      = mt_mod.ModelTrainer()
    draft_generator    = dg_mod.DraftGenerator(
        data_manager,
        signature="Best regards,\nThe Projector Support Team"
    )

    data_manager.load_responses()

    # ── Train or load model
    model_path = config["model_path"]

    if os.path.exists(model_path) and "--retrain" not in sys.argv:
        print(f"\n📦 Found existing model — loading from {model_path}")
        model_trainer.load_model(model_path)
    else:
        print("\n🎓 Training model from scratch...")
        with open(config["training_emails_path"], "r") as f:
            training_emails = json.load(f)

        texts, labels = model_trainer.prepare_training_data(training_emails, text_preprocessor)
        model_trainer.train_model(texts, labels)
        model_trainer.evaluate_model(texts, labels)
        model_trainer.save_model(model_path)

    if "--train-only" in sys.argv:
        print("\n✅ Training complete. Exiting.")
        return

    # ── Initialize Outlook connector (optional)
    outlook = None
    outlook_cfg = config.get("outlook", {})
    client_id = outlook_cfg.get("client_id", "")

    if client_id and client_id != "YOUR_CLIENT_ID_HERE":
        print("\n🔐 Connecting to Outlook...")
        outlook = oc_mod.OutlookConnector(
            client_id=client_id,
            tenant_id=outlook_cfg.get("tenant_id", "consumers"),
            token_cache_path="data/token_cache.json"
        )
        if not outlook.authenticate():
            print("⚠️  Outlook connection failed. Running without Outlook.")
            outlook = None
    else:
        print("\n⚠️  Outlook not configured — running in manual mode.")
        print("   (Add your CLIENT_ID to config.json to enable Outlook)")

    # ── Initialize classifier and interface
    classifier = cl_mod.EmailClassifier(model_trainer, text_preprocessor, data_manager)
    interface  = ui_mod.EmailInterface(classifier, draft_generator, data_manager, outlook)

    print("\n✅ System ready!\n")
    interface.run()


if __name__ == "__main__":
    main()
