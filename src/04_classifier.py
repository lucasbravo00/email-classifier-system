"""
Classifier: Classification of new emails
Responsibilities:
- Classify emails into predefined categories
- Calculate prediction confidence
- Explain predictions
"""

from typing import Dict, Optional


CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence to trust a prediction


class EmailClassifier:
    """Email classifier"""

    def __init__(self, model_trainer, text_preprocessor, data_manager):
        """
        Initialize the classifier

        Args:
            model_trainer: Instance of ModelTrainer with trained model
            text_preprocessor: Instance of TextPreprocessor
            data_manager: Instance of DataManager (to look up response details)
        """
        self.model_trainer = model_trainer
        self.text_preprocessor = text_preprocessor
        self.data_manager = data_manager

    def classify_email(self, subject: str, body: str) -> Dict:
        """
        Classify an email and return full result with response details

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Dict with:
              - response_id: int
              - confidence: float (0-1)
              - needs_review: bool (True if confidence is below threshold)
              - response: dict (full response from DataManager)
        """
        processed_text = self._preprocess_email(subject, body)
        response_id_str, confidence = self.model_trainer.predict(processed_text)

        if response_id_str is None:
            return {
                "response_id": None,
                "confidence": 0.0,
                "needs_review": True,
                "response": None,
                "message": "❌ Model not trained yet"
            }

        response_id = int(response_id_str)
        needs_review = confidence < CONFIDENCE_THRESHOLD
        response = self.data_manager.get_response_by_id(response_id)

        if needs_review:
            print(f"⚠️  Low confidence ({confidence:.1%}) — flagged for manual review")
        else:
            print(f"✅ Classified as response #{response_id} with {confidence:.1%} confidence")

        return {
            "response_id": response_id,
            "confidence": confidence,
            "needs_review": needs_review,
            "response": response
        }

    def get_confidence(self, subject: str, body: str) -> float:
        """
        Get confidence score for prediction

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Confidence value between 0 and 1
        """
        processed_text = self._preprocess_email(subject, body)
        _, confidence = self.model_trainer.predict(processed_text)
        return confidence

    def explain_prediction(self, subject: str, body: str) -> Dict:
        """
        Explain why the model chose that category

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Dict with explanation
        """
        processed_text = self._preprocess_email(subject, body)
        response_id_str, confidence = self.model_trainer.predict(processed_text)
        response_id = int(response_id_str)
        response = self.data_manager.get_response_by_id(response_id)

        # Find which words from the email match keywords in the response
        email_words = set(processed_text.split())
        keywords = set(response.get("keywords", []))
        matching_keywords = email_words & keywords

        return {
            "response_id": response_id,
            "response_title": response.get("title") if response else None,
            "confidence": confidence,
            "processed_text": processed_text,
            "matching_keywords": list(matching_keywords),
            "explanation": (
                f"Matched response #{response_id} ('{response.get('title')}') "
                f"with {confidence:.1%} confidence. "
                f"Matching keywords: {list(matching_keywords) if matching_keywords else 'none (learned from training data)'}"
            )
        }

    def _preprocess_email(self, subject: str, body: str) -> str:
        """
        Preprocess email for classification

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Processed text
        """
        return self.text_preprocessor.preprocess_email(subject, body)
