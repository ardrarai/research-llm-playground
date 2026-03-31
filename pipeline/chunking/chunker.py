import re
from pipeline.chunking.adaptive_chunker import adaptive_chunk_document


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


def fixed_chunk_document(text: str, chunk_size: int, overlap: int):
    """
    Sentence-aware fixed-size chunking with character-based overlap.
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


def chunk_document(
    text: str,
    chunk_size: int,
    overlap: int,
    *,
    chunk_mode: str = "fixed",
    target_chunk_tokens: int = 600,
    chunk_overlap_sentences: int = 2
):
    """
    Unified chunking entrypoint.
    """

    text = clean_text(text)

    if chunk_mode == "adaptive":
        return adaptive_chunk_document(
            text=text,
            target_chunk_tokens=target_chunk_tokens,
            chunk_overlap_sentences=chunk_overlap_sentences
        )

    # Default: fixed mode
    return fixed_chunk_document(text, chunk_size, overlap)
