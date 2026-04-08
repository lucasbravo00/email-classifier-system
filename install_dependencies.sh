#!/bin/bash
# Run this script once to install all required dependencies
# Usage: bash install_dependencies.sh

echo "======================================"
echo "Installing Email Classifier Dependencies"
echo "======================================"

pip install --upgrade pip
pip install scikit-learn        # ML model (TF-IDF + Naive Bayes)
pip install msal                # Microsoft Authentication Library (for Outlook)
pip install requests            # HTTP requests

echo ""
echo "======================================"
echo "✅ All dependencies installed!"
echo "======================================"
echo ""
echo "Now you can run:"
echo "  python main.py"
