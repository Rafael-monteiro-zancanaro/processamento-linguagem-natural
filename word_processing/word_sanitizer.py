import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')


def sanitize_text(corpus: str) -> list[str]:
    print(f'Nltk está procurando por recursos em {nltk.data.path}');
    tokens = word_tokenize(corpus)
    tokens_lower = [token.lower() for token in tokens]
    stop_words = set(stopwords.words('portuguese'))
    tokens_no_stopwords = [word for word in tokens_lower if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens_lemmatized = [lemmatizer.lemmatize(word) for word in tokens_no_stopwords]
    tokens_cleaned = [word for word in tokens_lemmatized if word.isalnum()]
    return tokens_cleaned