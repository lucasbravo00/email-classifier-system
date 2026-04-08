"""
Model Trainer: Training the classification model
Responsibilities:
- Prepare training data
- Train Naive Bayes + TF-IDF model
- Evaluate performance
- Save/Load model
"""

import os
import json
import pickle
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


class ModelTrainer:
    """Trainer for the classification model"""

    def __init__(self):
        """Initialize the trainer"""
        self.pipeline = None   # TF-IDF + Naive Bayes combined
        self.classes = None    # List of category names
        self.is_trained = False

    def prepare_training_data(self, training_emails: list, text_preprocessor) -> Tuple[list, list]:
        """
        Prepare training data from emails and their response IDs

        Args:
            training_emails: List of {"subject", "body", "response_id"}
            text_preprocessor: Instance of TextPreprocessor

        Returns:
            Tuple (processed_texts, response_ids) ready for training
        """
        texts = []
        labels = []

        for email in training_emails:
            # Support both formats:
            # old: {"subject": ..., "body": ..., "response_id": ...}
            # new: {"text": ..., "label": ...}
            if "text" in email:
                processed = text_preprocessor.preprocess_email("", email.get("text", ""))
                label = str(email.get("label"))
            else:
                processed = text_preprocessor.preprocess_email(
                    email.get("subject", ""),
                    email.get("body", "")
                )
                label = str(email.get("response_id"))
            texts.append(processed)
            labels.append(label)

        print(f"✅ Prepared {len(texts)} training examples")
        print(f"   Categories found: {list(set(labels))}")
        return texts, labels

    def train_model(self, texts: list, labels: list) -> None:
        """
        Train Naive Bayes model with TF-IDF

        Args:
            texts: List of preprocessed training texts
            labels: List of corresponding response IDs (as strings)
        """
        if len(texts) == 0:
            print("❌ Error: No training data provided")
            return

        # Build a pipeline: TF-IDF vectorizer + Naive Bayes classifier
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),   # Use single words and pairs of words
                min_df=1,             # Minimum frequency for a word to be included
                max_features=5000     # Maximum number of features
            )),
            ('classifier', MultinomialNB(alpha=0.1))  # Naive Bayes with smoothing
        ])

        self.pipeline.fit(texts, labels)
        self.classes = list(set(labels))
        self.is_trained = True

        print(f"✅ Model trained successfully!")
        print(f"   Training examples: {len(texts)}")
        print(f"   Categories: {self.classes}")

    def evaluate_model(self, texts_test: list, labels_test: list) -> Dict:
        """
        Evaluate model with performance metrics

        Args:
            texts_test: Test texts (preprocessed)
            labels_test: Real labels for test texts

        Returns:
            Dictionary with metrics (accuracy, precision, recall, f1-score)
        """
        if not self.is_trained:
            print("❌ Error: Model not trained yet. Call train_model() first.")
            return {}

        predictions = self.pipeline.predict(texts_test)
        accuracy = accuracy_score(labels_test, predictions)
        report = classification_report(labels_test, predictions, output_dict=True)

        print(f"\n📊 Model Evaluation Results:")
        print(f"   Accuracy: {accuracy * 100:.1f}%")
        print(f"\n{classification_report(labels_test, predictions)}")

        return {
            "accuracy": accuracy,
            "report": report,
            "predictions": predictions.tolist()
        }

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict category for a single preprocessed text

        Args:
            text: Preprocessed email text

        Returns:
            Tuple (predicted_label, confidence_score)
        """
        if not self.is_trained:
            print("❌ Error: Model not trained yet.")
            return None, 0.0

        prediction = self.pipeline.predict([text])[0]
        probabilities = self.pipeline.predict_proba([text])[0]
        confidence = max(probabilities)

        return prediction, confidence

    def save_model(self, model_path: str) -> bool:
        """
        Save trained pipeline to disk

        Args:
            model_path: Path to save the model

        Returns:
            True if saved successfully
        """
        if not self.is_trained:
            print("❌ Error: Model not trained yet. Nothing to save.")
            return False

        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump({
                    "pipeline": self.pipeline,
                    "classes": self.classes
                }, f)
            print(f"✅ Model saved to {model_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving model: {str(e)}")
            return False

    def load_model(self, model_path: str) -> bool:
        """
        Load a previously saved pipeline from disk

        Args:
            model_path: Path of saved model

        Returns:
            True if loaded successfully
        """
        try:
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            self.pipeline = data["pipeline"]
            self.classes = data["classes"]
            self.is_trained = True
            print(f"✅ Model loaded from {model_path}")
            print(f"   Categories: {self.classes}")
            return True
        except FileNotFoundError:
            print(f"❌ Error: Model file not found at {model_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return False
