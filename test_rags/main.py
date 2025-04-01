# Load document into workflow for processing
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader

loader = DirectoryLoader("guides", glob="**/*.md", show_progress=True, use_multithreading=True)
docs = loader.load()
len(docs)