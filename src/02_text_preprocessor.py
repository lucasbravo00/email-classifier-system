"""
Text Preprocessor: Cleaning and preparing text for ML
Responsibilities:
- Clean text (URLs, special characters)
- Tokenization
- Remove stopwords
- Lemmatization
"""

import re
from typing import List, Dict


class TextPreprocessor:
    """Text processor for data preparation"""

    # Common English stopwords
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'as', 'if', 'so',
        'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its',
        'our', 'their', 'me', 'him', 'us', 'them', 'am', 'being', 'should'
    }

    # Simple lemmatization dictionary (common words and their base forms)
    LEMMA_DICT = {
        'starting': 'start', 'started': 'start', 'starts': 'start',
        'running': 'run', 'runs': 'run', 'ran': 'run',
        'helping': 'help', 'helps': 'help', 'helped': 'help',
        'working': 'work', 'works': 'work', 'worked': 'work',
        'watching': 'watch', 'watches': 'watch', 'watched': 'watch',
        'creating': 'create', 'creates': 'create', 'created': 'create',
        'uploading': 'upload', 'uploads': 'upload', 'uploaded': 'upload',
        'downloading': 'download', 'downloads': 'download', 'downloaded': 'download',
        'streaming': 'stream', 'streams': 'stream', 'streamed': 'stream',
        'setting': 'set', 'settings': 'setting', 'sets': 'set',
        'using': 'use', 'uses': 'use', 'used': 'use',
        'beginning': 'begin', 'begins': 'begin', 'began': 'begin',
        'trying': 'try', 'tries': 'try', 'tried': 'try',
        'installing': 'install', 'installs': 'install', 'installed': 'install',
        'playing': 'play', 'plays': 'play', 'played': 'play',
        'videos': 'video', 'movies': 'movie',
        'questions': 'question', 'problems': 'problem', 'issues': 'issue',
        'formats': 'format', 'files': 'file', 'devices': 'device',
        'accounts': 'account', 'services': 'service', 'options': 'option'
    }

    def __init__(self, language: str = "english"):
        """
        Initialize the preprocessor

        Args:
            language: Language for stopwords ("english", "spanish", etc)
        """
        self.language = language
        print(f"✅ TextPreprocessor initialized for {language}")

    def remove_urls(self, text: str) -> str:
        """
        Remove URLs from text

        Args:
            text: Text with possible URLs

        Returns:
            Text without URLs
        """
        # Remove http/https URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        # Remove www URLs
        text = re.sub(r'www\.[^\s]+', '', text)
        # Remove common domain patterns
        text = re.sub(r'[a-zA-Z0-9.-]+\.(com|org|net|edu|io)', '', text)
        return text

    def clean_text(self, text: str) -> str:
        """
        Clean text by removing URLs, special characters, etc

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Remove URLs first
        text = self.remove_urls(text)

        # Convert to lowercase
        text = text.lower()

        # Remove email addresses
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)

        # Remove special characters and numbers, keep only letters and spaces
        text = re.sub(r'[^a-z\s]', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Divide text into tokens (words)

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        try:
            # Simple tokenization by splitting on whitespace
            tokens = text.split()
            # Filter out empty tokens
            tokens = [token.strip() for token in tokens if token.strip()]
            return tokens
        except Exception as e:
            print(f"❌ Error tokenizing text: {str(e)}")
            return []

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove common words (stopwords)

        Args:
            tokens: List of tokens

        Returns:
            List of tokens without stopwords
        """
        filtered_tokens = [
            token for token in tokens
            if token.lower() not in self.STOPWORDS and len(token) > 1
        ]
        return filtered_tokens

    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Normalize words to their root form (lemma)

        Args:
            tokens: List of tokens

        Returns:
            List of lemmatized tokens
        """
        lemmatized_tokens = []
        for token in tokens:
            token_lower = token.lower()
            # Use the lemma dictionary if available, otherwise use the word as-is
            lemmatized_tokens.append(self.LEMMA_DICT.get(token_lower, token_lower))
        return lemmatized_tokens

    def preprocess_email(self, subject: str, body: str) -> str:
        """
        Complete preprocessing pipeline

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Processed text ready for ML
        """
        # Combine subject and body
        combined_text = f"{subject} {body}"

        # Step 1: Clean text
        cleaned = self.clean_text(combined_text)

        # Step 2: Tokenize
        tokens = self.tokenize(cleaned)

        # Step 3: Remove stopwords
        filtered = self.remove_stopwords(tokens)

        # Step 4: Lemmatize
        lemmatized = self.lemmatize(filtered)

        # Step 5: Join back into string
        final_text = ' '.join(lemmatized)

        return final_text
