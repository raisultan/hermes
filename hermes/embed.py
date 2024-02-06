"""Everything needed to make an embedding."""

import asyncio
import os
from itertools import islice
from typing import Generator, Iterable

import tiktoken
from openai import AsyncOpenAI as OpenAI
from dotenv import load_dotenv

from hermes.crawler.logger import logger

EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191  # a.k.a. CHUNK_SIZE, CHUNK_LENGTH, MAX_TOKENS
EMBEDDING_ENCODING = 'cl100k_base'


load_dotenv(override=True)

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


async def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    """Get the embedding for the given text."""
    response = await client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


# Copied from: https://cookbook.openai.com/examples/embedding_long_inputs
def batched(iterable: Iterable, n: int) -> Generator[tuple, None, None]:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while (batch := tuple(islice(it, n))):
        yield batch


def chunked_tokens(text: str, encoding_name: str, chunk_length: int) -> Generator[list[str], None, None]:
    """Chunk text into tokens of length chunk_length."""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks_iterator = batched(tokens, chunk_length)
    yield from chunks_iterator


async def get_len_safe_embeddings(
    text: str,
    model: str = EMBEDDING_MODEL,
    max_tokens: str = EMBEDDING_CTX_LENGTH,
    encoding_name: str = EMBEDDING_ENCODING,
) -> list[list[float]]:
    """Get the embeddings for the given text, chunked into safe lengths."""
    embeddings = []

    chunks = [chunk for chunk in chunked_tokens(text, encoding_name=encoding_name, chunk_length=max_tokens)]
    tasks = [get_embedding(chunk, model) for chunk in chunks]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.error(f'Error getting embedding: {repr(result)}')
        else:
            embeddings.append(result)

    return embeddings
