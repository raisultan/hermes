## Hermes -- Semantic Document Search System

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

## Making it faster
Input: 2 pdfs with < 30 pages
1 - Straight forward approach of inserting pdfs consequently takes - 79s
2 - Making the worker and the function async - 79s
3 - Async with asyncio.gather - 79s
4 - Each pdf in its own process using concurrent.futures.ProcessPoolExecutor - 96s
5 - Using concurrent approach with AsyncOpenAI client (improvements made described below) - ~10s

## Improving PDF ingestion design
### Current approach
For each pdf file:
    1 - pdf_extract - extracts each page's content in loop and returns list of PDFPages -> pages
    2 - For each page in PDFPages:
        2.1 - normalize(page.content) - it normalizes content of page -> normalized
        2.2 - get_len_safe_embedding(normalized) -> embeddings:
            2.2.1 - chunks text using generator with yield, for each chunk:
                2.2.1.1 - get_embedding(chunk, model) - makes API call to OpenAI to get embedding vector
                2.2.1.2 - puts each embedding to list
            2.2.2 - returns list of embeddings
        2.3 - for each embedding in embeddings -> records:
            2.3.1 - prepare record to be inserted to milvus
            2.3.2 - put that record in a list

There are a lot of improvements to be made to current approach. First thing we really need and that must be done synchronously is to parse the single pdf file and get it's pages. After we get list of pages we can start triggering concurrent/parallel jobs. Let's think about data ingestion in terms of single page. So, for each page we need:
1 - normalization
2 - split a page into chunks
3 - for each chunk we need to get an embedding
4 - for each embedding we prep it for insertion and insert it

Here are tasks and their types that are made by the algorithm:
1 - Parsing pdfs using pdfium: mostly I/O bound due to reads and writes to disk.
2 - Embedding: pure I/O bound, cause it is an API call.
3 - Insertion to DB: I/O bound.

This tells that we need to use either ThreadPoolExecutor or asyncio. We don't need ProcessPoolExecutor cause there is no need for separate Python interpreters to do CPU bound tasks.

Let's try asyncio approach that operates in terms of a single page and run that job for each page concurrently.

## Todo
* Readme
* Make faster pdf ingestion

## Use
* Run the app with providing path to folder where pdfs are located
* Crawler periodically checks new pdfs and uploads them into Vector DB
* App provides API to search those PDFs and cites sources
