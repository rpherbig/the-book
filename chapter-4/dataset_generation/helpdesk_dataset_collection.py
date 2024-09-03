from .dataset_generator import DatasetGenerator
from .generate_helpdesk_requests import data_location

# entity, so top level dict -- "mechanic": {
# irrelevant                --     "dealership operated young mechanic": {
# category 1, what we want  --         "Their login credentials are not working ": {
# category 2, stretch goal  --           "because they are not typing them correctly.": [
# datapoint list     "Subject: Re: Login Credentials Issue\nHi IT Team,\n\nI am trying to log in to the sales portal, but my credentials are not working. I've tried multiple times, but it keeps saying my username or password is incorrect. Can you please assist me with this issue?\n\nThank you,\n[Young Mechanic at Dealership]\n\n---\n\nSubject: Re: Login Credentials Issue\nHi [Young Mechanic],\n\nThank you for reaching out. Are you sure you are typing in your username and password correctly? Please double-check and try again. If the issue persists, let us know.\n\nBest regards,\nIT Team\n\n---\n\nSubject: Re: Login Credentials Issue\nHi IT Team,\n\nI apologize for the inconvenience, but it seems I was indeed not typing in my credentials correctly. I have successfully logged in now. Thank you for your prompt assistance.\n\nKind regards,\n[Young Mechanic]"
#     ],

class HelpdeskDatasetCollection():
    @staticmethod
    def build_flattened_user_dataset(dict):
        flattened = {}
        labels = {}
        label_index = 1
        for __specialized_user, categories_dict in dict.items():
            for category, specialized_category_dict in categories_dict.items():
                flattened[category] = []
                if category not in labels:
                    labels[category] = label_index
                    label_index += 1
                for __specialized_category, datapoints_list in specialized_category_dict.items():
                    flattened[category] += (datapoints_list)
        return flattened, labels
    
    @staticmethod
    def reverse_dict(dict):
        ret = {}
        for key, value in dict.items():
            ret[value] = key
        return ret


    def __init__(self, origin_dictionary):
        self.user_datasets = {}
        self.user_labels_hr_to_int = {}
        self.user_labels_int_to_hr = {}
        self.ml_dict = None
        for base_user, dict in origin_dictionary.items():
            data, labels = HelpdeskDatasetCollection.build_flattened_user_dataset(dict)
            self.user_datasets[base_user] = data
            self.user_labels_hr_to_int[base_user] = labels
            self.user_labels_int_to_hr[base_user] = HelpdeskDatasetCollection.reverse_dict(labels)
        self.build_ml_sets()

    def build_ml_sets(self):
        # assume training, test set split happens down stream
        # [user]['labels']
        # [user]['data']
        if self.ml_dict is not None:
            return self.ml_dict
        # TODO: dict from user type -> dataset
        ret = {}
        for user_id, user_data in self.user_datasets.items():
            this_user = []
            for category, datapoints in user_data.items():
                label = self.user_labels_hr_to_int[user_id][category]
                this_user += list(map(lambda datapoint: (label, datapoint,), datapoints))
            ret[user_id] = this_user
        self.ml_dict = ret
        return self.ml_dict
    
    @staticmethod
    def load(path):
        generated_data = DatasetGenerator.load(path)
        return HelpdeskDatasetCollection(generated_data.results)    
