## Semantic Document Search System

### Overview
This project presents a robust and scalable solution for semantic search across a corpus of PDF documents given in a local folder and subfolders. Utilizing the power of Milvus, a vector database, it offers an efficient way to find relevant documents based on the semantic content of the queries. The system is designed with a focus on modularity and ease of extensibility to accommodate future enhancements.

### Components
1. Document Processing Component
    - Purpose: To handle the extraction and preprocessing of text from PDF documents.
    - Sub-Components:
        - PDF Text Extractor: Extracts raw text from PDF files.
        - Text Preprocessor: Cleans and normalizes the extracted text.
2. Embedding Component
    - Purpose: To convert preprocessed text into vector representations using an NLP model.
    - Sub-Components:
        - Embedding Model Loader: Loads the selected NLP model.
        - Vectorizer: Converts text into embeddings using the model.
3. Database Integration Component
    - Purpose: To manage interactions with the Milvus database.
    - Sub-Components:
        - Database Connector: Establishes connection and manages interactions with Milvus.
        - Data Ingestor: Handles the ingestion of document embeddings into the database.
4. API Component
    - Purpose: To provide interfaces for adding new documents and performing semantic searches.
    - Sub-Components:
        - Document Ingestion API: Allows for adding new documents to the system.
        - Search API: Enables semantic search over the embedded documents.

## Similar Projects
- [Search In PDF Doc - Full Stack App](https://medium.com/@dbabbs/guide-create-a-full-stack-semantic-search-web-app-with-custom-documents-edeae2b35b3c)
- [Semantic Search with Retrieve and Rerank](https://huggingface.co/spaces/nickmuchi/semantic-search-with-retrieve-and-rerank/tree/main)

## Todo
* Crawler - find pdfs in dir and sub-dirs and load them into DB
* Extract -> Embed -> Insert pipeline optimization
* How to evaluate search?
