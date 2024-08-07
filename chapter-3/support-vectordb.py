from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma.vectorstores import Chroma
from dotenv import load_dotenv
import os
import shutil

load_dotenv()

CHROMA_PATH = "chroma"
DATA_PATH = "data"

print("Cleaning up temporary files")
if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)

loader = DirectoryLoader(DATA_PATH, glob="*.md")
documents = loader.load()
print(f"Loaded {len(documents)} documents into memory.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,
    chunk_overlap=25,
    length_function=len,
    add_start_index=True,
)
chunks = text_splitter.split_documents(documents)
print(f"Split documents into {len(chunks)} chunks.")
first_chunk = chunks[0]
print(f"First chunk's content: {first_chunk.page_content}")
print(f"First chunk's metadata: {first_chunk.metadata}")

db = Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH)
print("Saved chunks to the vector database")
