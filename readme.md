## Hermes - Semantic Document Search

![hermes](hermes.jpg)

## Overview
Hermes is specifically designed to facilitate the efficient and effective search of documents within a specified folder and its subfolders. At its core, the system boasts a user-friendly and straightforward API, making it accessible for users to search and retrieve information seamlessly. One of the standout features of Hermes is its ability to not only identify relevant documents but also cite the specific sources, pinpointing the exact page number and presenting the associated content. This feature enhances the user's experience by providing detailed and precise search results. Furthermore, the system is optimized for speed and smooth operation, ensuring that searches through extensive collections of PDF documents are conducted swiftly and results are delivered promptly. The combination of these features makes Hermes an ideal solution for those seeking a local document search system that is both efficient and thorough.

## Components
1. **API:** provides an interface search PDFs and to set directory path in which PDFs are located
2. **Crawler:** periodically checks and ingests PDFs into Vector DB if there are any changes in dir itself or in sub-dirs

## Use
1. Run Milvus Vector DB
```bash
docker compose -f milvus-docker-compose.yaml up -d
```
2. Run the API component
```bash
make run-web
```
3. Using API and API docs on `http://127.0.0.1:8000/docs` use `POST /api/dir_path` endpoint to set the path to PDFs dir
4. Run the Crawler
```bash
make run-crawler
```
5. Use the API to query PDFs

## Progress of Work

### Improving PDF Ingestion Design
#### Current Approach
For each pdf file:
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

#### PDF ingestion timings
Input: 2 pdfs with < 30 pages
1. Straight forward approach of inserting pdfs consequently takes - 79s
2. Making the worker and the function async - 79s
3. Async with `asyncio.gather` - 79s
4. Each pdf in its own process using `concurrent.futures.ProcessPoolExecutor` - 96s
5. Using concurrent approach with AsyncOpenAI client (improvements made described below) - ~10s


### Todo
- Better logging
