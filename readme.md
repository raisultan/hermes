## Hermes - Semantic Document Search

## Overview
Hermes simplifies document searching within specified directories, offering precise and quick retrieval of PDF documents. By combining a user-friendly API with powerful search capabilities, Hermes highlights relevant documents and their exact locations, facilitating efficient information access.

## Key Components
- **API:** Facilitates searching within PDFs and setting the directory path for the PDFs.
- **Crawler:** Automatically updates the database with new or modified PDFs by monitoring specified directories.

## Getting Started
### Prerequisites
- Docker
- Make

## Setup
1. **Start Milvus Vector DB**
```bash
docker compose -f milvus-docker-compose.yaml up -d
```
2. **Run the API component**
```bash
make run-web
```
3. **Configure PDF Directory Path**\
Navigate to `http://127.0.0.1:8000/docs` and use the POST `/api/dir_path` endpoint to specify the path to your PDFs directory.
4. **Launch the Crawler**
```bash
make run-crawler
```
5. **Query Your PDFs**
Utilize the API to perform your document searches.

## Progress of Work

### Enhancing PDF Ingestion
#### Old Approach
For each PDF:
1. `pdf_extract` - extracts each page's content in a loop and returns a list of PDFPages -> pages
2. For each page in PDFPages:
   1. `normalize(page.content)` - normalizes content of the page -> normalized
   2. `get_len_safe_embedding(normalized)` -> embeddings:
      1. Chunks text using a generator with yield, for each chunk:
         1. `get_embedding(chunk, model)` - makes an API call to OpenAI to get the embedding vector
         2. Puts each embedding into a list
      2. Returns the list of embeddings
   3. For each embedding in embeddings:
      1. Prepares a record to be inserted into Milvus
      2. Puts that record in a list

#### Making Things Faster

There are a lot of improvements to be made to current approach. First thing we really need and that must be done synchronously is to parse the single pdf file and get its pages. After we get a list of pages we can start triggering concurrent/parallel jobs. Let's think about data ingestion in terms of a single page. So, for each page we need:
1. Normalization
2. Split a page into chunks
3. For each chunk we need to get an embedding
4. For each embedding we prep it for insertion and insert it

Here are tasks and their types that are made by the algorithm:
1. Parsing pdfs using pdfium: mostly I/O bound due to reads and writes to disk.
2. Embedding: pure I/O bound, cause it is an API call.
3. Insertion to DB: I/O bound.

This tells that we need to use either `ThreadPoolExecutor` or `asyncio`. We don't need `ProcessPoolExecutor` cause there is no need for separate Python interpreters to do CPU bound tasks.

Let's try `asyncio` approach that operates in terms of a single page and run that job for each page concurrently.

After refactoring it takes almost 10x less time to ingest PDFs into Vector DB.

#### PDF Ingestion Timings
Input: 2 pdfs with < 30 pages
- Initial sequential approach: ~79 seconds
- Improved concurrent approach with `AsyncOpenAI` client: ~10 seconds
