from .dataset_generator import DatasetGenerator
from .generate_funeral_home_reviews import negative_review_users, data_location

class FuneralHomeDatasetCollection():
    
    labels_hr_to_int = {
        "positive" : 0,
        "negative" : 1
    }

    labels_int_to_hr = {
        0 : "positive",
        1 : "negative"
    }

    def build_labeled_dataset(self, dict):
        flattened = {
            self.labels_hr_to_int["positive"] : [],
            self.labels_hr_to_int["negative"] : []
        }
        for __user, categories_dict in dict.items():
            for specialized_user, specialized_category_dict in categories_dict.items():
                specialization = specialized_user.split(" ")[0]
                label = 1 if specialization in negative_review_users else 0
                #print(specialized_user, specialization, label)
                for __specialized_category, datapoints_list in specialized_category_dict.items():
                    for sentences in datapoints_list.values():
                        flattened[label] += sentences
        self.ml_dict = flattened
        return self.ml_dict

    def __init__(self, origin_dictionary):
        self.build_labeled_dataset(origin_dictionary)

    def split_X_y(self):
        X = []
        y = []
        for label, datapoints in self.ml_dict.items():
            for datum in datapoints:
                X.append(datum)
                y.append(label)
        return X, y

    @staticmethod
    def load(path):
        generated_data = DatasetGenerator.load(path)
        return FuneralHomeDatasetCollection(generated_data.results)    
