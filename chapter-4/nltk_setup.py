import nltk

"""
Installs data packages needed by nltk for the other parts of the code to work.
Think of it as an addendum to requirements.txt
"""

if __name__ == "__main__":
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')