# Email Classification System - Help Center

Intelligent system for automatically classifying incoming emails into predefined categories and generating response drafts ready for review.

## Description

This system uses **Machine Learning** (scikit-learn) to:
1. Receive incoming emails
2. Automatically classify them into one of the predefined responses
3. Generate a draft with the appropriate response
4. Show to user for review before sending

## Project Structure

```
email-classifier-system/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.json                  # Configuration
├── main.py                      # Main script
├── src/
│   ├── 01_data_manager.py       # Response management
│   ├── 02_text_preprocessor.py  # Text cleaning
│   ├── 03_model_trainer.py      # Model training
│   ├── 04_classifier.py         # Email classification
│   ├── 05_draft_generator.py    # Draft generation
│   └── 06_interface.py          # User interface
├── data/
│   ├── responses.json           # Response database
│   ├── test_emails.json         # Test emails
│   ├── trained_model.pkl        # Trained ML model
│   └── vectorizer.pkl           # Vectorizer
└── tests/
    ├── test_preprocessing.py
    ├── test_classification.py
    └── test_full_pipeline.py
```

## Installation

### 1. Clone the project
```bash
cd email-classifier-system
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Prepare predefined responses

Create file `data/responses.json` with structure:

```json
[
  {
    "id": 170,
    "category": "Getting Started",
    "keywords": ["start", "begin", "new account"],
    "title": "How do I start",
    "description": "An explanation of how to start",
    "body": "It is very easy to start. What you want to do is..."
  },
  {
    "id": 130,
    "category": "Video Quality",
    "keywords": ["streaming", "video format"],
    "title": "Video Streaming Standards",
    "description": "Video Streaming Standards",
    "body": "To ensure the best performance..."
  }
]
```

### Step 2: Train the model

```bash
python main.py
# Select option: 1 (Train model)
```

### Step 3: Process emails

```bash
python main.py
# Select option: 2 (Process email)
# Paste incoming email
# System proposes response
# User reviews and confirms
```

## Modules

### 01_data_manager.py
Manages predefined response database

**Main functions:**
- `load_responses()` - Load responses from JSON
- `get_response_by_id()` - Get specific response
- `get_all_categories()` - List categories

### 02_text_preprocessor.py
Cleans and prepares text for machine learning

**Main functions:**
- `clean_text()` - Remove URLs, special characters
- `tokenize()` - Split into words
- `remove_stopwords()` - Remove common words
- `preprocess_email()` - Complete pipeline

### 03_model_trainer.py
Trains the classification model

**Main functions:**
- `train_model()` - Train Naive Bayes + TF-IDF
- `evaluate_model()` - Calculate performance
- `save_model()` - Save model
- `load_model()` - Load model

### 04_classifier.py
Classifies new emails

**Main functions:**
- `classify_email()` - Predict category + confidence
- `get_confidence()` - Get confidence score
- `explain_prediction()` - Explain prediction

### 05_draft_generator.py
Creates response drafts

**Main functions:**
- `generate_draft()` - Create complete draft
- `personalize_response()` - Add client name
- `add_signature()` - Add signature

### 06_interface.py
User interface

**Main functions:**
- `show_email_input()` - Receive email
- `show_prediction()` - Show classification
- `show_draft()` - Show draft
- `confirm_and_send()` - User confirmation

## Features

✅ Automatic email classification
✅ Machine Learning with scikit-learn
✅ Secure response storage (JSON)
✅ Manual review before sending
✅ Confidence calculation in predictions
✅ Continuous feedback collection for improvement

## Testing

```bash
# Run unit tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_preprocessing.py -v
```

## Performance Metrics

The model is evaluated with:
- **Precision:** How many predictions were correct?
- **Recall:** How many emails of each category did we identify?
- **F1-Score:** Balance between precision and recall

## Security

- Responses stored in `data/responses.json` (read-only during normal use)
- Model trained once and reused
- Every email reviewed by a human before sending
- No automatic sending, always under user control

## Configuration

Edit `config.json` to adjust:
- `confidence_threshold`: Minimum confidence to use prediction (default: 0.7)
- `language`: Language for stopwords
- File paths

## Notes

- System designed for maximum 50 predefined responses
- Compatible with Python 3.8+
- Requires ~100MB RAM
- Training time: < 5 seconds

## Contributing

To add new responses:
1. Edit `data/responses.json`
2. Retrain model: `python main.py` → option 1
3. Ready to use

## Contact

For questions or suggestions about this system, contact your manager.

## License

Internal - Projector Help Center
