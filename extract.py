import pypdfium2 as pdfium

def pdf_extract(path: str) -> str:
    pdf = pdfium.PdfDocument(path)
    pages_content = [p.get_textpage().get_text_range() for p in pdf]
    return "\n".join(pages_content)
