from extract import pdf_extract
from embed import get_len_safe_embeddings
from load import prepare_record, insert

def run(path: str):
    text = pdf_extract(path)
    embeddings = get_len_safe_embeddings(text)
    for embedding in embeddings:
        prepare_record(path, text, embeddings)
