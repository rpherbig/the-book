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

text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=25)
chunks = text_splitter.split_documents(documents)
print(f"Split documents into {len(chunks)} chunks.")
for chunk in chunks:
    print(f"Chunk content: \"{chunk.page_content}\" from source \"{chunk.metadata["source"]}\"")

embedding_function = OpenAIEmbeddings()
db = Chroma.from_documents(chunks, embedding_function, persist_directory=CHROMA_PATH)
print("Saved chunks to the vector database")
