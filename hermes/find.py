import os


def pdf_find(dir: str) -> list[str]:
    pdf_files = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files
