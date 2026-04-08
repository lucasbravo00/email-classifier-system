"""
Test script for DataManager module
Tests all 5 functions to ensure they work correctly
"""

import sys
import importlib.util

# Load the module dynamically since it starts with a number
spec = importlib.util.spec_from_file_location("data_manager", "src/01_data_manager.py")
data_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_manager_module)
DataManager = data_manager_module.DataManager

def main():
    print("=" * 60)
    print("Testing DataManager Module")
    print("=" * 60)

    # Initialize DataManager with the path to responses.json
    dm = DataManager("data/responses.json")

    # TEST 1: Validate JSON
    print("\n[TEST 1] Validating JSON file...")
    is_valid = dm.validate_json()
    assert is_valid, "JSON validation failed"
    print("✅ TEST 1 PASSED\n")

    # TEST 2: Load responses
    print("[TEST 2] Loading responses...")
    responses = dm.load_responses()
    assert len(responses) > 0, "No responses loaded"
    assert len(responses) == 2, f"Expected 2 responses, got {len(responses)}"
    print("✅ TEST 2 PASSED\n")

    # TEST 3: Get all categories
    print("[TEST 3] Getting all categories...")
    categories = dm.get_all_categories()
    assert len(categories) == 2, f"Expected 2 categories, got {len(categories)}"
    assert "Getting Started" in categories, "Missing 'Getting Started' category"
    assert "Video Quality" in categories, "Missing 'Video Quality' category"
    print("✅ TEST 3 PASSED\n")

    # TEST 4: Get response by ID
    print("[TEST 4] Getting response by ID...")

    # Get response 170
    response_170 = dm.get_response_by_id(170)
    assert response_170 is not None, "Response 170 not found"
    assert response_170["category"] == "Getting Started", "Wrong category for response 170"
    assert response_170["title"] == "How do I start", "Wrong title for response 170"

    # Get response 130
    response_130 = dm.get_response_by_id(130)
    assert response_130 is not None, "Response 130 not found"
    assert response_130["category"] == "Video Quality", "Wrong category for response 130"
    assert response_130["title"] == "Video Streaming Standards", "Wrong title for response 130"

    # Try to get non-existent response
    response_999 = dm.get_response_by_id(999)
    assert response_999 is None, "Should return None for non-existent response"
    print("✅ TEST 4 PASSED\n")

    # TEST 5: Add new response
    print("[TEST 5] Adding new response...")
    new_response = {
        "id": 200,
        "category": "Billing",
        "title": "How to pay",
        "description": "Payment methods",
        "keywords": ["payment", "billing", "subscribe"],
        "body": "To pay for our service, you can use credit card or PayPal."
    }

    result = dm.add_response(new_response)
    assert result, "Failed to add new response"

    # Verify it was added
    added_response = dm.get_response_by_id(200)
    assert added_response is not None, "Added response not found"
    assert added_response["category"] == "Billing", "Added response has wrong category"

    # Try to add duplicate
    result_dup = dm.add_response(new_response)
    assert not result_dup, "Should not allow duplicate IDs"
    print("✅ TEST 5 PASSED\n")

    # Summary
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nDataManager is working correctly!")
    print(f"- Loaded responses: {len(dm.responses)}")
    print(f"- Categories: {dm.get_all_categories()}")
    print(f"- Response IDs: {[r['id'] for r in dm.responses]}")


if __name__ == "__main__":
    main()
