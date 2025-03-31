from utils.vectorstore import VectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

template = """
You are a helpful assistant that can answer questions about the text provided.
If you don't know the answer, just say "I don't know".
Use 10 sentences minimum and keep the answer concise.
Question:
{question}
Context:
{context}
Answer:
"""

vectorstore = VectorStore("data/sample.txt", chunk_size=250, chunk_overlap=50)

prompt= ChatPromptTemplate.from_template(template)
output_parser = StrOutputParser()
llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rag_chain = ({"context": vectorstore.get_db().as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | llm_model
    | output_parse

print(rag_chain.invoke("What is Ashu AI"))