# General Process Workflow
- First implement RAG agent 
- Next, connect RAG agent to an api endpoint
- Finally, connect api endpoint to a frontend (If needed)

## RAG Agent Implementation Steps
- Collect manuals / schematics / troubleshooting guides _/_/_/
- Pass into RAG workflow
    - Chunk documents
    - Embed Chunks
    - Store embeded chunks into vector DB
    - Setup retrieval & similarity search 
    - Augment LLM result 
- Set workflow as an Agent
- Create a realtime search Agent also
- Implement features to combact Naive RAG
  