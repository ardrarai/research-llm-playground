import re
from statistics import mean, stdev


def sentence_tokenize(text: str):
    """
    Split text into sentences (lightweight, deterministic).
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def estimate_tokens(text: str):
    """
    Approximate token count using word length heuristic.
    Stable and model-agnostic.
    """
    return max(1, int(len(text.split()) * 1.3))


def detect_section_boundary(sentence: str):
    """
    Heuristic detection of section boundaries.
    """
    sentence_upper = sentence.strip().upper()

    if len(sentence) < 80 and (
        sentence_upper.isupper()
        or re.match(r"^\d+(\.\d+)*\s+", sentence)
        or sentence_upper.startswith((
            "INTRODUCTION",
            "METHOD",
            "MATERIAL",
            "RESULT",
            "DISCUSSION",
            "CONCLUSION",
            "BACKGROUND"
        ))
    ):
        return True

    return False


def adaptive_chunk_document(
    text: str,
    target_chunk_tokens: int = 600,
    chunk_overlap_sentences: int = 2,
    min_chunks: int = 50,
    max_chunks: int = 150
):
    """
    Adaptive, sentence-aware chunking with stability control.
    """

    sentences = sentence_tokenize(text)

    if not sentences:
        return []

    sentence_tokens = [estimate_tokens(s) for s in sentences]
    total_tokens = sum(sentence_tokens)

    # Determine target chunk count
    approx_chunks = total_tokens / target_chunk_tokens
    target_chunks = int(min(max(approx_chunks, min_chunks), max_chunks))
    target_tokens_per_chunk = total_tokens / target_chunks

    chunks = []
    current_chunk = []
    current_tokens = 0

    for idx, sentence in enumerate(sentences):

        sent_tokens = sentence_tokens[idx]
        boundary = detect_section_boundary(sentence)

        # Decide whether to flush chunk
        if (
            current_chunk
            and (
                current_tokens + sent_tokens > target_tokens_per_chunk * 1.15
                or boundary
            )
        ):
            chunks.append(" ".join(current_chunk))

            # Apply sentence-based overlap
            if chunk_overlap_sentences > 0:
                current_chunk = current_chunk[-chunk_overlap_sentences:]
                current_tokens = sum(
                    estimate_tokens(s) for s in current_chunk
                )
            else:
                current_chunk = []
                current_tokens = 0

        current_chunk.append(sentence)
        current_tokens += sent_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
