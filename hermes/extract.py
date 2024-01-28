from dataclasses import dataclass

import pypdfium2 as pdfium


@dataclass
class PDFPage:
    num: int
    content: str
    path: str


def pdf_extract(path: str) -> list[PDFPage]:
    pdf = pdfium.PdfDocument(path)
    pages = []
    for num, page in enumerate(pdf, start=1):
        content = page.get_textpage().get_text_range()
        pages.append(PDFPage(num, content, path))
    return pages
