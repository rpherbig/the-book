from dataset_generation.generate_helpdesk_requests import add_to_dataset as new_helpdesk_requests
from dataset_generation.generate_funeral_home_reviews import add_to_dataset as new_funeral_home_reviews

"""
Produces datasets for topic extraction and sentiment analysis using OpenAI's API
You'll need to put your api key in openai.key for this code to run.
"""

if __name__ == "__main__":
    new_funeral_home_reviews()
    new_helpdesk_requests()