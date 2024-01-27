import os
from itertools import islice

import tiktoken
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191  # a.k.a. CHUNK_SIZE, CHUNK_LENGTH, MAX_TOKENS
EMBEDDING_ENCODING = 'cl100k_base'


load_dotenv(override=True)

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    return client.embeddings.create(input=text, model=model).data[0].embedding


# Copied from: https://cookbook.openai.com/examples/embedding_long_inputs
def batched(iterable, n):
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while (batch := tuple(islice(it, n))):
        yield batch


def chunked_tokens(text, encoding_name, chunk_length):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks_iterator = batched(tokens, chunk_length)
    yield from chunks_iterator


def get_len_safe_embeddings(
        text: str,
        model: str = EMBEDDING_MODEL,
        max_tokens: str = EMBEDDING_CTX_LENGTH,
        encoding_name: str = EMBEDDING_ENCODING,
        average: bool = False,
    ):
    chunk_embeddings = []
    chunk_lens = []
    for chunk in chunked_tokens(text, encoding_name=encoding_name, chunk_length=max_tokens):
        embedding = get_embedding(chunk, model)
        chunk_embeddings.append(embedding)
        chunk_lens.append(len(chunk))

    if average:
        chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)  # normalizes length to 1
        chunk_embeddings = chunk_embeddings.tolist()
    return chunk_embeddings
