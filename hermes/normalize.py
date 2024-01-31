import re


def normalize(text: str) -> str:
    """Normalize text for embedding."""
    # Normalize character encoding to UTF-8
    text = text.encode('utf-8', errors='replace').decode('utf-8')

    # Handle line breaks and hyphenation:
    # Replace hyphens followed by a newline with an empty string
    text = re.sub(r'-\n', '', text)
    # Replace newlines not preceded by a period with a space
    text = re.sub(r'(?<!\.)\n', ' ', text)

    # Convert to lowercase for consistency
    text = text.lower()

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Trim leading and trailing white spaces
    text = text.strip()

    # Remove or Replace Special Characters (if they don't carry semantic value)
    # Example: remove special characters except periods and commas
    text = re.sub(r'[^\w\s.,]', '', text)

    return text
