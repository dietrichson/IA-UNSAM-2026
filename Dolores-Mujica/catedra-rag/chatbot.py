import os
import sys
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 1. Cargar documentos de la carpeta 'datos'
loader = DirectoryLoader('./datos', glob="./*.txt", loader_cls=TextLoader)
documents = loader.load()

# 2. Dividir el texto en fragmentos (chunks)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# 3. Crear embeddings y guardar en base vectorial local
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(docs, embeddings)

# 4. Configurar el modelo de lenguaje y la memoria del chat
llm = Ollama(model="qwen2.5:3b")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    memory=memory
)

print("--- Asistente de Cátedra listo. Escribe 'salir' para terminar. ---")
while True:
    pregunta = input("\nAlumno: ")
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        break
    respuesta = qa_chain.run(pregunta)
    print(f"\nAsistente: {respuesta}")
