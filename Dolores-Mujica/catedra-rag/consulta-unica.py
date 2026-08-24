import sys
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# Verificar que se pase una pregunta como argumento
if len(sys.argv) < 2:
    print("Uso: python consulta-unica.py \"Tu pregunta aquí\"")
    sys.exit(1)

pregunta = sys.argv[1]

# 1. Cargar documentos
loader = DirectoryLoader('./datos', glob="./*.txt", loader_cls=TextLoader)
documents = loader.load()

# 2. Dividir el texto
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# 3. Embeddings y base de vectores
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(docs, embeddings)

# 4. Configurar modelo y cadena RAG
llm = Ollama(model="llama3")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# 5. Ejecutar la consulta
respuesta = qa_chain.run(pregunta)
print(f"\nRespuesta:\n{respuesta}")
