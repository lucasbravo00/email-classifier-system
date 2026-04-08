"""
Test script for TextPreprocessor module
Tests all 6 functions to ensure they work correctly
"""

import importlib.util

# Load the module dynamically
spec = importlib.util.spec_from_file_location("text_preprocessor", "src/02_text_preprocessor.py")
text_preprocessor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(text_preprocessor_module)
TextPreprocessor = text_preprocessor_module.TextPreprocessor


def main():
    print("=" * 70)
    print("Testing TextPreprocessor Module")
    print("=" * 70)

    # Initialize TextPreprocessor
    tp = TextPreprocessor(language="english")
    print("\n✅ TextPreprocessor initialized with English stopwords\n")

    # TEST 1: Remove URLs
    print("[TEST 1] Removing URLs...")
    test_text_url = "Check out https://projector.help and www.example.com for info"
    result = tp.remove_urls(test_text_url)
    expected = "Check out  and  for info"
    assert "https" not in result and "www" not in result, "URLs not removed"
    print(f"  Input:  {test_text_url}")
    print(f"  Output: {result}")
    print("✅ TEST 1 PASSED\n")

    # TEST 2: Clean text
    print("[TEST 2] Cleaning text...")
    test_text_clean = "How do I START?!? Visit https://projector.help for info!!!"
    result = tp.clean_text(test_text_clean)
    assert "https" not in result, "URL not removed in clean_text"
    assert "?" not in result, "Special characters not removed"
    assert result == result.lower(), "Text not converted to lowercase"
    assert "  " not in result, "Extra spaces not removed"
    print(f"  Input:  {test_text_clean}")
    print(f"  Output: {result}")
    print("✅ TEST 2 PASSED\n")

    # TEST 3: Tokenize
    print("[TEST 3] Tokenizing text...")
    test_text_token = "how do i start projector"
    result = tp.tokenize(test_text_token)
    assert isinstance(result, list), "Tokenize should return a list"
    assert len(result) > 0, "No tokens returned"
    assert "how" in result, "Expected token 'how' not found"
    print(f"  Input:  {test_text_token}")
    print(f"  Output: {result}")
    print("✅ TEST 3 PASSED\n")

    # TEST 4: Remove stopwords
    print("[TEST 4] Removing stopwords...")
    test_tokens = ["how", "do", "i", "start", "projector"]
    result = tp.remove_stopwords(test_tokens)
    assert "how" not in result, "Stopword 'how' not removed"
    assert "do" not in result, "Stopword 'do' not removed"
    assert "i" not in result, "Stopword 'i' not removed"
    assert "start" in result, "Important word 'start' was removed"
    assert "projector" in result, "Important word 'projector' was removed"
    print(f"  Input:  {test_tokens}")
    print(f"  Output: {result}")
    print("✅ TEST 4 PASSED\n")

    # TEST 5: Lemmatize
    print("[TEST 5] Lemmatizing tokens...")
    test_tokens_lem = ["starting", "running", "helping", "worked"]
    result = tp.lemmatize(test_tokens_lem)
    assert "start" in result, "Lemmatization of 'starting' failed"
    assert "run" in result, "Lemmatization of 'running' failed"
    assert "help" in result, "Lemmatization of 'helping' failed"
    print(f"  Input:  {test_tokens_lem}")
    print(f"  Output: {result}")
    print("✅ TEST 5 PASSED\n")

    # TEST 6: Complete preprocessing pipeline
    print("[TEST 6] Complete preprocessing pipeline...")
    subject = "How do I START?!?"
    body = "I want to BEGIN using Projector. Visit https://projector.help for more info!!!"
    result = tp.preprocess_email(subject, body)

    print(f"  Subject: {subject}")
    print(f"  Body:    {body}")
    print(f"  Output:  {result}")

    # Verify results
    assert isinstance(result, str), "Output should be a string"
    assert "start" in result, "Expected 'start' in output"
    assert "begin" in result, "Expected 'begin' in output"
    assert "projector" in result, "Expected 'projector' in output"
    assert "https" not in result, "URL not removed"
    assert "?" not in result, "Special characters not removed"
    assert "how" not in result, "Stopword 'how' not removed"
    assert result == result.lower(), "Output not lowercase"

    print("✅ TEST 6 PASSED\n")

    # Additional test: Different email examples
    print("[TEST 7] Testing with real email examples...")

    # Example 1: Getting Started email
    email1_subject = "How to get started with Projector?"
    email1_body = """Hi, I just found out about Projector and I want to know how to start using it.
    Can you explain the steps? I want to begin uploading videos to my account.
    Visit https://www.projectorstream.com for more information."""

    result1 = tp.preprocess_email(email1_subject, email1_body)
    print(f"  Email 1 Result: {result1}")
    assert "start" in result1, "Should contain 'start'"
    assert "projector" in result1, "Should contain 'projector'"

    # Example 2: Video Quality email
    email2_subject = "Video streaming quality issues"
    email2_body = """I'm having problems with video quality when I try to stream.
    What are the correct file formats and codecs I should use?
    Please visit https://projector.help/gettingstarted/#video-streaming"""

    result2 = tp.preprocess_email(email2_subject, email2_body)
    print(f"  Email 2 Result: {result2}")
    assert "video" in result2, "Should contain 'video'"
    assert "quality" in result2, "Should contain 'quality'"

    print("✅ TEST 7 PASSED\n")

    # Summary
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\nTextPreprocessor is working correctly!")
    print("- All text cleaning functions work properly")
    print("- Tokenization, stopword removal, and lemmatization work")
    print("- Complete pipeline produces clean, normalized text")
    print("- Ready to be used by ModelTrainer and Classifier")


if __name__ == "__main__":
    main()
