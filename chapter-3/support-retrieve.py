from dotenv import load_dotenv
from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""
# Answer the question based on the above context and include the source for that answer: {question}

embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

while True:
    user_input = input("Enter the user prompt (or type 'exit' to quit):")
    if user_input.lower() == "exit":
        break
    
    print("Retrieving similar text")
    results = db.similarity_search_with_relevance_scores(user_input)
    print(f"Found {len(results)} matching results:")
    for (document, confidence) in results:
        print(f"Found \"{document.page_content}\" in source \"{document.metadata["source"]}\" with confidence {confidence}")
    
    print("Building context from similar text")
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    # context_text = "\n\n---\n\n".join([f"Answer: \"{doc.page_content}\"; Source: \"{doc.metadata["source"]}\"" for doc, _ in results])
    print("Building prompt from context")
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=user_input)
    print(f"Prompt: {prompt}")

    model = ChatOpenAI()
    response = model.invoke(prompt)
    print(f"Response: {response.content}")
