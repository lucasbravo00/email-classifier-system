"""
Data Manager: Manages the database of predefined responses
Responsibilities:
- Load responses from JSON
- Validate data integrity
- Provide access to specific responses
"""

import json
import os
from typing import List, Dict, Optional


class DataManager:
    """Manager for predefined responses"""

    def __init__(self, responses_path: str):
        """
        Initialize the data manager

        Args:
            responses_path: Path to JSON file with responses
        """
        self.responses_path = responses_path
        self.responses = []

    def load_responses(self) -> List[Dict]:
        """
        Load responses from JSON file

        Returns:
            List of dictionaries with the responses
        """
        try:
            with open(self.responses_path, 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
            print(f"✅ Successfully loaded {len(self.responses)} responses from {self.responses_path}")
            return self.responses
        except FileNotFoundError:
            print(f"❌ Error: File not found at {self.responses_path}")
            return []
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON format in {self.responses_path}")
            return []
        except Exception as e:
            print(f"❌ Error loading responses: {str(e)}")
            return []

    def get_response_by_id(self, response_id: int) -> Optional[Dict]:
        """
        Get a specific response by ID

        Args:
            response_id: ID of the response

        Returns:
            Dictionary with the response or None if not found
        """
        if not self.responses:
            print("⚠️  Warning: No responses loaded. Call load_responses() first.")
            return None

        for response in self.responses:
            if response.get("id") == response_id:
                print(f"✅ Found response with ID {response_id}")
                return response

        print(f"❌ Response with ID {response_id} not found")
        return None

    def get_all_categories(self) -> List[str]:
        """
        Get all unique response categories

        Returns:
            List of unique categories
        """
        if not self.responses:
            print("⚠️  Warning: No responses loaded. Call load_responses() first.")
            return []

        categories = []
        seen = set()

        for response in self.responses:
            category = response.get("category")
            if category and category not in seen:
                categories.append(category)
                seen.add(category)

        print(f"✅ Found {len(categories)} unique categories: {categories}")
        return categories

    def add_response(self, response: Dict) -> bool:
        """
        Add a new response

        Args:
            response: Dictionary with the new response

        Returns:
            True if added successfully
        """
        # Validate that response has required fields
        required_fields = ["id", "category", "title", "body"]
        missing_fields = [field for field in required_fields if field not in response]

        if missing_fields:
            print(f"❌ Error: Response missing required fields: {missing_fields}")
            return False

        # Check if ID already exists
        if self.get_response_by_id(response.get("id")) is not None:
            print(f"❌ Error: Response with ID {response.get('id')} already exists")
            return False

        # Add the response
        self.responses.append(response)
        print(f"✅ Successfully added response with ID {response.get('id')}")
        return True

    def validate_json(self) -> bool:
        """
        Validate that the JSON file is valid

        Returns:
            True if valid, False if errors
        """
        try:
            with open(self.responses_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if it's a list
            if not isinstance(data, list):
                print("❌ Error: JSON must contain a list of responses")
                return False

            # Check each response
            required_fields = ["id", "category", "title", "body"]
            for idx, response in enumerate(data):
                if not isinstance(response, dict):
                    print(f"❌ Error: Response at index {idx} is not a dictionary")
                    return False

                missing_fields = [field for field in required_fields if field not in response]
                if missing_fields:
                    print(f"❌ Error: Response at index {idx} missing fields: {missing_fields}")
                    return False

            print(f"✅ JSON is valid! Contains {len(data)} responses")
            return True
        except FileNotFoundError:
            print(f"❌ Error: File not found at {self.responses_path}")
            return False
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON format in {self.responses_path}")
            return False
        except Exception as e:
            print(f"❌ Error validating JSON: {str(e)}")
            return False
