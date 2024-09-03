from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dataset_generation.generate_funeral_home_reviews import data_location
from dataset_generation.funeral_home_dataset_collection import FuneralHomeDatasetCollection

"""
A custom sentiment lexicon for use in VADER sentiment analysis
"""
custom_lexicon_path = "data/funeral_home_lexicon.txt"

def label_text(reviews, analyzer):
    """
    Labels the text according to the sentiment of the text

    reviews - the text to be labeled
    analyzer - the function to be analyzed
    returns - the compound valence for each piece of text analyzed in order.
    """
    res = []
    for review in reviews:
        valence = analyzer.polarity_scores(review)
        label = 0 if valence['compound'] > 0 else 1
        valence['label'] = label
        res.append(valence)
    return res


def score(texts, truths, analyzer):
    """
    Computes sentiment and scores the analyzer by comparing it to ground truth

    texts - the text to be analyzed
    truths - ground truth about the sentiment of the document
    analyzer - the function doing sentiment analysis
    returns - dictionary of scored texts according to true positive, true negative, false positive, false negative
    """
    labels = label_text(texts, analyzer)
    res = {
        "true_positive" : [],
        "true_negative" : [],
        "false_positive" : [],
        "false_negative" : []
    }
    for index, (sentiments, truth) in enumerate(zip(labels, truths)):
        label = sentiments["label"]
        if label == 1 and truth == 1:
            res["true_positive"].append(index)
        elif label == 0 and truth == 0:
            res["true_negative"].append(index)
        elif label == 1 and truth == 0:
            res["false_positive"].append(index)
        elif label == 0 and truth == 1:
            res["false_negative"].append(index)
        else:
            raise Exception(f"Label and truth should be restricted to 0 & 1, got label {label}, truth {truth}")
    return res           


def summarize(scores):
    """
    Compute accuracy metrics of sentiment analysis given the scores

    scores -- computed sentiment and true sentiment of the documents as a dictionary
    returns - a dictionary containing precision, recall, and f1 score
    """
    res = {}
    for key, values in scores.items():
        res[key] = len(values)
    precision = res['true_positive'] / (res['true_positive'] + res['false_positive'])
    recall = res['true_positive'] / (res['true_positive'] + res['false_negative'])
    f1 = 2 * precision * recall / (precision + recall)
    res['precision'] = precision
    res['recall'] = recall
    res['f1'] = f1
    return res


def show_examples(texts, scores, count=10):
    """
    Show examples of false positives and false negatives

    texts - the texts that were evaluated
    scores - the sentiments attached to each of them
    count -- the maximum number to display
    """
    print("False Positives")
    print("\n===========False Positives=================\n")
    for index in scores['false_positive'][:count]:
        print(texts[index])
    print("\n\n=========False Negatives=================\n")
    print("False Negatives")
    for index in scores['false_negative'][:count]:
        print(texts[index])
    print("\n===========================================\n")


def evaluate(analyzer, dataset, display = True):
    """
    Evaluate the analyzer on the dataset

    analyzer - the sentiment analyzer to evaluate
    dataset - a collection of texts to analyze
    display - should we pretty-print the results
    returns summary of scores and explicit scoring details
    """
    texts, truths = dataset.split_X_y()
    scores = score(texts, truths, analyzer)
    summary = summarize(scores)
    if display:
        print(summary)
        show_examples(texts, scores)
    return summary, scores


if __name__ == "__main__":
    dataset = FuneralHomeDatasetCollection.load(data_location)
    lexicon_path = Path(custom_lexicon_path)
    analyzer = SentimentIntensityAnalyzer(lexicon_file=lexicon_path.absolute())
    analyzer_base = SentimentIntensityAnalyzer()
    customized_summary, customized_scores = evaluate(analyzer, dataset)
    base_summary, base_scores = evaluate(analyzer_base, dataset)
