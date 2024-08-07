import time
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
example_query = "How do I contact the Maintenance & Service department?"
os.remove(".langchain.db")
os.remove("similar_cache/faiss.index")
os.remove("similar_cache/sqlite.db")
os.rmdir("similar_cache")

print("Example 1, a simple in-memory cache using a Python dictionary with an exact match")

cache = {}

def main(user_query):
    if user_query in cache.keys():
        return cache[user_query]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content":
                """
                You are a customer service chatbot designed to be helpful and answer user's questions if possible.
                The phone number for the Maintenance & Service department is (555) 555-1234.
                The phone number for the Customer Support department is (555) 555-5678.
                The phone number for the Dealer Service department is (555) 555-9012.
                The hours of operation for the Maintenance & Service department are 7am-7pm every day.
                The hours of operation for the Customer Support department are 8am-5pm every weekday.
                The hours of operation for the Dealer Service department are 7am-6pm every weekday and noon-5pm on Saturdays.
                """
            },
            {"role": "user", "content": user_query},
        ]
    )
    cache[user_query] = completion.choices[0].message.content

perf_start = time.perf_counter()
main(example_query)
perf_end = time.perf_counter()
print(f"First execution, with no caching: {perf_end - perf_start} seconds")

perf_start = time.perf_counter()
main(example_query)
perf_end = time.perf_counter()
print(f"Second execution, with a cache hit: {perf_end - perf_start} seconds")

print("-----")
from langchain.globals import set_llm_cache
from langchain_openai import OpenAI
from langchain_community.cache import SQLiteCache
print("Example 2, a more realistic SQLite DB cache using the Langchain library with an exact match")

llm = OpenAI(model_name="gpt-3.5-turbo-instruct")
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

perf_start = time.perf_counter()
t = llm.invoke(example_query)
perf_end = time.perf_counter()
print(f"First execution, with no caching: {perf_end - perf_start} seconds")

perf_start = time.perf_counter()
llm.invoke(example_query)
perf_end = time.perf_counter()
print(f"Second execution, with a cache hit: {perf_end - perf_start} seconds")

print("-----")
print("Example 3, using the GPTCache library with a semantic similarity match (not exact!) on embeddings")
from gptcache.adapter.api import init_similar_cache
from langchain_community.cache import GPTCache

def init_gptcache(cache_obj):
    init_similar_cache(cache_obj=cache_obj, data_dir=f"similar_cache")

set_llm_cache(GPTCache(init_gptcache))

perf_start = time.perf_counter()
t = llm.invoke(example_query)
perf_end = time.perf_counter()
print(f"First execution, with no caching: {perf_end - perf_start} seconds")

perf_start = time.perf_counter()
llm.invoke(example_query.replace("contact", "reach"))
perf_end = time.perf_counter()
print(f"Second execution, with a cache hit: {perf_end - perf_start} seconds")
