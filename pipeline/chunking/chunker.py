import re


def clean_text(text: str):
    """
    Remove low-value sections like acknowledgments and references.
    """

    patterns_to_remove = [
        r"Acknowledgments.*",
        r"References.*",
        r"Institutional Review Board Statement.*",
        r"Data Availability Statement.*",
        r"Funding:.*"
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    return text


def chunk_document(text: str, chunk_size: int, overlap: int):
    """
    Sentence-aware chunking with overlap.
    """

    text = clean_text(text)

    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())

            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + " " + sentence
            else:
                current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
