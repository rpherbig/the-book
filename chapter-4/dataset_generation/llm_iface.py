import os
from openai import OpenAI

class Client:

    client = None
    n = 3
    def __init__(self, n=3):
        self.n = n
        self.get_client()


    @staticmethod
    def grab_api_key(key_loc="./openai.key"):
        key = None
        if os.path.exists(key_loc):
            with open(key_loc, "r") as f:
                key = f.read().strip()
        return key


    def get_client(self):
        if self.client is None:
            self.client = OpenAI(api_key=self.grab_api_key())


    @staticmethod
    def system_message(message):
        return {
            "role": "system",
            "content": message,
        }


    @staticmethod
    def user_message(message):
        return {
            "role": "user",
            "content": message,
        }


    def query(self, preamble, request):
        chat_completion = self.client.chat.completions.create(
        messages=[
            self.system_message(preamble),
            self.user_message(request),
        ],
        n=self.n,
        model="gpt-3.5-turbo",
        )
        return chat_completion
