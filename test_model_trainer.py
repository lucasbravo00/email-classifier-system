"""
Test script for ModelTrainer module
Run this from the project root: python test_model_trainer.py
Requires: pip install scikit-learn
"""

import json
import importlib.util
import os


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    print("=" * 70)
    print("Testing ModelTrainer Module")
    print("=" * 70)

    # Load modules
    tp_module = load_module("text_preprocessor", "src/02_text_preprocessor.py")
    mt_module = load_module("model_trainer", "src/03_model_trainer.py")

    TextPreprocessor = tp_module.TextPreprocessor
    ModelTrainer = mt_module.ModelTrainer

    tp = TextPreprocessor()
    mt = ModelTrainer()

    # Load training emails
    with open("data/training_emails.json", "r") as f:
        training_emails = json.load(f)

    print(f"\n📂 Loaded {len(training_emails)} training emails")

    # TEST 1: Prepare training data
    print("\n[TEST 1] Preparing training data...")
    texts, labels = mt.prepare_training_data(training_emails, tp)
    assert len(texts) == len(training_emails), "Mismatch in training data length"
    assert len(set(labels)) == 2, f"Expected 2 categories, got {len(set(labels))}"
    print("✅ TEST 1 PASSED\n")

    # TEST 2: Train model
    print("[TEST 2] Training model...")
    mt.train_model(texts, labels)
    assert mt.is_trained, "Model should be trained"
    assert mt.pipeline is not None, "Pipeline should exist"
    print("✅ TEST 2 PASSED\n")

    # TEST 3: Evaluate model (using training data as simple check)
    print("[TEST 3] Evaluating model...")
    metrics = mt.evaluate_model(texts, labels)
    assert "accuracy" in metrics, "Metrics should include accuracy"
    assert metrics["accuracy"] >= 0.7, f"Accuracy too low: {metrics['accuracy']}"
    print("✅ TEST 3 PASSED\n")

    # TEST 4: Predict on new emails
    print("[TEST 4] Testing predictions on new emails...")

    test_cases = [
        {
            "subject": "I'm new, how do I start?",
            "body": "Hi, I just heard about Projector and want to start using it.",
            "expected": "170"
        },
        {
            "subject": "Video quality problem",
            "body": "My videos look terrible when streaming. What format should I use?",
            "expected": "130"
        }
    ]

    for case in test_cases:
        processed = tp.preprocess_email(case["subject"], case["body"])
        prediction, confidence = mt.predict(processed)
        print(f"  Subject: {case['subject']}")
        print(f"  Predicted: {prediction} (confidence: {confidence:.1%})")
        print(f"  Expected:  {case['expected']}")
        assert prediction == case["expected"], f"Wrong prediction: got {prediction}, expected {case['expected']}"
        assert confidence > 0.5, f"Confidence too low: {confidence}"
        print()

    print("✅ TEST 4 PASSED\n")

    # TEST 5: Save and reload model
    print("[TEST 5] Saving and reloading model...")
    save_path = "data/trained_model.pkl"
    result = mt.save_model(save_path)
    assert result, "Model save failed"
    assert os.path.exists(save_path), "Model file not created"

    # Load into a fresh instance
    mt2 = ModelTrainer()
    loaded = mt2.load_model(save_path)
    assert loaded, "Model load failed"
    assert mt2.is_trained, "Loaded model should be trained"

    # Verify loaded model gives same predictions
    processed = tp.preprocess_email("How do I start?", "I want to begin using Projector")
    pred1, conf1 = mt.predict(processed)
    pred2, conf2 = mt2.predict(processed)
    assert pred1 == pred2, "Loaded model gives different predictions"
    print("✅ TEST 5 PASSED\n")

    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print(f"\nModel is ready!")
    print(f"- Trained on {len(training_emails)} emails")
    print(f"- Categories: {mt.classes}")
    print(f"- Accuracy: {metrics['accuracy'] * 100:.1f}%")
    print(f"- Saved to: {save_path}")


if __name__ == "__main__":
    main()
