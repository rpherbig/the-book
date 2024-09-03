import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from dataset_generation.generate_helpdesk_requests import data_location
from dataset_generation.helpdesk_dataset_collection import HelpdeskDatasetCollection


"""
Custom stop words
We're mostly discrading punctuation
"""
custom_stops = set([
    '.',
    '!',
    '?',
    '-',
    ',',
    '--',
    ':',
    '[',
    ']',
])


def process_text(original, stemmer, stops):
    """
    Tokenizes, stems, and lemmatizes a piece of text. Also removes stop words.

    text - the text to produce a simplified version of
    stops - set of stop words that do not encode in the output
    lemmatizer - function for lemmatizing words in text
    returns - a set of tokens representing the simplafied text
    """
    tokens = nltk.word_tokenize(original)
    stems = []
    for token in tokens:
        token = token.lower()
        if token not in stops and token not in custom_stops:
            stems.append(stemmer.stem(token))
    return stems


def get_tfidf(data, stemmer, stops):
    """
    Computes term-frequency inverse document frequency for a document set

    data - raw strings
    stemmer - produced stemmed version of words
    stops - words to not encode in embedding
    returns TF/IDF vectorizer and an embedding of all text in the data
    """
    embedder = TfidfVectorizer(tokenizer=lambda x : process_text(x, stemmer, stops))
    tfidf = embedder.fit_transform(map(lambda x: x[1], data))
    return embedder, tfidf


def frequency_sort(frequency_dict, top=None):
    """
    Sorts a dictionary of (key, value) pairs by value, which in this setting represents frequency

    frequency_dict - the dictionary to sort the keys
    top - the number of leading values to return, or None for not trucnating
    returns a list of (value, key) pairs, sorted by valuet_data
    """
    as_pairs = []
    for key, value in frequency_dict.items():
        as_pairs.append((value, key))
    as_pairs.sort(reverse=True, key=lambda tup: tup[0])
    if top is None:
        return as_pairs
    else:
        return as_pairs[:top]


def _single_value_decomposition(embedder, text_tfidf, num_classes):
    """
    Performs single value decomposition on a single document

    embedder - the tool for embedding text into tf/idf vectors
    text_tfidf - an embedding of the text in tf/idf
    num_classes - the number of topics / classes to try and recover
    returns frequency sorted list of topics
    """
    corpus_svd = TruncatedSVD(n_components=num_classes)
    svd_result = corpus_svd.fit_transform(text_tfidf)
    ret = {}
    for feat_name, score in zip(embedder.get_feature_names_out(), corpus_svd.components_[0]):
        ret[feat_name] = score
    return frequency_sort(ret, num_classes)


def single_value_decomposition(embedder, embedded_texts, num_classes=10):
    """
    Performs single value decomposition on all documents in a collection
    
    embedder - the tool for embedding text into tf/idf vectors
    embedded_texts - all documents embedded by tf/idf
    num_classes - the number of topics / classes to try and recover
    returns frequency sorted list of topics for each document in the corpus
    """
    ret = []
    for embedded_text in embedded_texts:
        ret.append(_single_value_decomposition(embedder, embedded_text, num_classes))
    return ret


def _tf(text, stemmer, stops, num_classes):
    """
    Computes term frequency for a piece of text

    text - text to compute term frequency on
    stemmer - function to stem & lemmatize words
    stops - words to not encode
    num_classes - expected number of topics or classes
    returns - frequency sorted list of topics
    """
    tokens = process_text(text, stemmer, stops)
    ret = {}
    for token in tokens:
        if token not in ret:
            ret[token] = 1
        else:
            ret[token] += 1
    return frequency_sort(ret, num_classes)


def tf(texts, stemmer, stops, num_classes=10):
    """
    Computes term frequency for all texts in a corpus

    texts -- all texts in a corpus
    stemmer - function to stem & lemmatize words
    stops - words to not encode
    num_classes - expected number of topics or classes
    returns - frequency sorted list of topics for each document in corpus
    """
    ret = []
    for text in texts:
        ret.append(_tf(text, stemmer, stops, num_classes))
    return ret


if __name__ == "__main__":
    dataset = HelpdeskDatasetCollection.load(data_location)
    stemmer = nltk.stem.PorterStemmer()
    stops = set(stopwords.words('english')).union(custom_stops)
    num_topics = 3
    for user, data in dataset.ml_dict.items():
        true_labels = list(map(lambda x: x[0], data))
        texts = list(map(lambda x: x[1], data))
        num_classes = len(dataset.user_labels_hr_to_int[user])
        embedder, tfidf = get_tfidf(data, stemmer, stops)
        tf_topics = tf(texts, stemmer, stops, num_topics)
        svd_topics = single_value_decomposition(embedder, tfidf, num_topics)
        print(f"Did embedding for {user}")
        for document, tf_res, svd_res in zip(texts, tf_topics, svd_topics):
            print(document[:25])
            print("TF:", tf_res)
            print("SVD", svd_res)
