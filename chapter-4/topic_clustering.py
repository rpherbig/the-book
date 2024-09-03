import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
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


def cluster(n_clusters, tfidf):
    """
    Performs agglomerative clustering on the tfidf matrix

    n_clusters - the number of topics we expect to find
    tfidf - The term frequency / inverse document frequency embedding of the corpus
    returns - the computed clustering and a map of documents to cluster ids (numbers)
    """
    res = {}
    clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(tfidf.toarray())
    for index, id in enumerate(clustering.labels_):
        id = int(id)
        if id in res:
            res[id].append(index)
        else:
            res[id] = [index]
    return clustering, res


def compute_majority_label(cluster_true_labels):
    """
    Computes the majority label for a cluster
    cluster_true_labels - the true labels for the documents in a cluster
    returns - the majority label for the cluster
    """
    frequencies = {}
    for x in cluster_true_labels:
        if x in frequencies:
            frequencies[x] += 1
        else:
            frequencies[x] = 0
    majority_label = None
    majority_label_count = 0
    for x, count in frequencies.items():
        if count > majority_label_count:
            majority_label = x
            majority_label_count = count
    return majority_label


def score(cluster_labels, ground_truth):
    """
    Scores the clustering accuracy based on ground truth topics of underlying documents

    cluster_labels -- the computed labels from Agglomorative Clustering
    ground_truth -- the cluster labels from the dataset
    returns - hits, misses, and majority label for each computed cluster
    """
    res = {}
    for cluster_id, indexes in cluster_labels.items():
        cluster_true_labels = list(map(lambda x: ground_truth[x], indexes))
        majority_label = compute_majority_label(cluster_true_labels)
        hits = []
        misses = []
        for index, truth in zip(indexes, cluster_true_labels):
            if truth == majority_label:
                hits.append(index)
            else:
                misses.append(index)
        res[cluster_id] = {
            "majority_label" : majority_label,
            "hits" : hits,
            "misses" : misses
        }
    return res


def pretty_print_scores(score):
    """
    Pretty prints the scores for each cluster

    score -- the scores to print
    """
    sorted_keys = list(score.keys())
    sorted_keys.sort()
    for key in sorted_keys:
        print(key, score[key])
        

if __name__ == "__main__":
    dataset = HelpdeskDatasetCollection.load(data_location)
    stemmer = nltk.stem.PorterStemmer()
    stops = set(stopwords.words('english')).union(custom_stops)
    for user, data in dataset.ml_dict.items():
        true_labels = list(map(lambda x: x[0], data))
        num_classes = len(dataset.user_labels_hr_to_int[user])
        embedder, tfidf = get_tfidf(data, stemmer, stops)
        clustering, groupings = cluster(num_classes, tfidf)
        evaluation = score(groupings, true_labels)
        pretty_print_scores(evaluation)