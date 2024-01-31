import os


def pdf_find(dir: str) -> list[str]:
    """Find all PDF files in the given directory and subdirectories."""
    pdf_files = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files
