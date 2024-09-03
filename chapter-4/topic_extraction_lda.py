from gensim import corpora
from gensim.models.ldamodel import LdaModel
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

from dataset_generation.generate_helpdesk_requests import data_location
from dataset_generation.helpdesk_dataset_collection import HelpdeskDatasetCollection


def token_and_lemmatize(text, stops, lemmatizer):
    """
    Tokenizes, stems, and lemmatizes a piece of text. Also removes stop words.

    text - the text to produce a simplified version of
    stops - set of stop words that do not encode in the output
    lemmatizer - function for lemmatizing words in text
    returns - a set of tokens representing the simplafied text
    """
    tokens = []
    for candidate_token in nltk.word_tokenize(text):
        if len(candidate_token) < 3:
            continue
        if candidate_token in stops:
            continue
        tokens.append(lemmatizer(candidate_token))
    return tokens


def build_lda_model(texts, num_topics):
    """
    Builds the Latent Dirichlet Allocation (LDA) model of the provided texts

    texts - a list of strings to be modeled with LDA
    num_topics - the number of topics we suspect are present in the text
    returns - a model of all of the texts and the lda model in a dictionary
    """
    lemmatizer = WordNetLemmatizer().lemmatize
    stops = set(stopwords.words('english'))
    prepped = [ token_and_lemmatize(text, stops, lemmatizer) for text in texts ]
    dictionary = corpora.Dictionary(prepped)
    corpus = [ dictionary.doc2bow(text) for text in prepped ]
    model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary)
    return {
        "corpus" : corpus,
        "model" : model
    }


def get_topics(texts, num_topics):
    """
    Displays the topics we believe to be present for each piece of text in the corpus
    along with a snippet of the text to which the categories belong

    texts - a list of strings to be modeled with LDA
    num_topics - the number of topics we expect are present in the text

    """
    lda_model = build_lda_model(texts, num_topics)
    for raw_text, bow in zip(texts, lda_model["corpus"]):
        topics = lda_model["model"].get_document_topics(bow)
        print(raw_text[:25])
        print(topics)


if __name__ == "__main__":
    dataset = HelpdeskDatasetCollection.load(data_location)
    stemmer = nltk.stem.PorterStemmer()
    num_topics = 3
    for user, data in dataset.ml_dict.items():
        true_labels = list(map(lambda x: x[0], data))
        texts = list(map(lambda x: x[1], data))
        get_topics(texts, num_topics)