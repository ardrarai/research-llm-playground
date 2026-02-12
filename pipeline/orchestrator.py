import re
from utils.pdf_loader import load_pdf
from pipeline.chunking.chunker import chunk_document
from pipeline.embedding.embedder import embed_chunks
from pipeline.retrieval.retriever import retrieve
from pipeline.generation.generator import generate_answer
from pipeline.evaluation.metrics import compute_metrics


# ---------------------------------------------------
# GAP SENTENCE EXTRACTION
# ---------------------------------------------------

def extract_gap_sentences(chunks, max_sentences=12):
    """
    Extract sentences likely indicating research gaps.
    """

    keywords = [
        "limitation",
        "limitations",
        "future",
        "further",
        "challenge",
        "lack",
        "insufficient",
        "gap",
        "needed",
        "requires",
        "should",
        "not become widespread",
        "could not",
        "cannot",
        "remains unclear",
        "yet to be",
        "uncertain",
        "not fully effective",
        "active area for future research"
    ]

    filtered_sentences = []

    for chunk in chunks:
        sentences = re.split(r'(?<=[.!?])\s+', chunk)

        for sentence in sentences:
            sentence_clean = sentence.strip().lower()

            if any(keyword in sentence_clean for keyword in keywords):
                filtered_sentences.append(sentence.strip())

    return filtered_sentences[:max_sentences]


# ---------------------------------------------------
# CONTEXT SIZE CONTROL
# ---------------------------------------------------

def cap_context_length(sentences, max_chars=2500):
    """
    Prevent local LLM slowdown by hard-capping context size.
    """

    combined = ""
    selected = []

    for sentence in sentences:
        if len(combined) + len(sentence) > max_chars:
            break
        combined += sentence + " "
        selected.append(sentence)

    return selected

def compute_overlap(list_a, list_b):
    """
    Compute Jaccard similarity between two lists.
    """
    set_a = set(list_a)
    set_b = set(list_b)

    if not set_a and not set_b:
        return 1.0

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)

    return round(len(intersection) / len(union), 3)


# ---------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------

def run_pipeline(config, document_path, query):

    # 1️⃣ Load PDF
    text = load_pdf(document_path)

    # 2️⃣ Chunk
    chunks = chunk_document(text, config.chunk_size, config.chunk_overlap)

    # 3️⃣ Embed
    vectors, embed_time = embed_chunks(chunks, config.embedding_model)

    # 4️⃣ Retrieve
    retrieved_chunks, scores = retrieve(
        query,
        vectors,
        chunks,
        config.retrieval_mode,
        config.top_k
    )

    # 5️⃣ Gap-aware filtering
    filtered_context = extract_gap_sentences(retrieved_chunks)

    # 6️⃣ Cap context size for LLM stability
    if filtered_context:
        context_for_generation = cap_context_length(filtered_context)
    else:
        # fallback to first few raw chunks (also capped)
        fallback_sentences = retrieved_chunks[:3]
        context_for_generation = cap_context_length(fallback_sentences)

    # 7️⃣ Generate
    output, gen_time = generate_answer(
        query,
        context_for_generation,
        config.temperature,
        config.prompt_mode
    )

    # 8️⃣ Latency tracking
    latency = {
        "embedding_time": embed_time,
        "generation_time": gen_time
    }

    # 9️⃣ Metrics
    metrics = compute_metrics(retrieved_chunks, output, latency)

    # 🔟 Additional debug metadata
    debug_info = {
        "total_chunks_created": len(chunks),
        "retrieved_count": len(retrieved_chunks),
        "filtered_sentence_count": len(filtered_context),
        "context_sentences_used": len(context_for_generation)
    }

    return {
        "output": output,
        "retrieved_chunks": retrieved_chunks,
        "filtered_context": filtered_context,
        "scores": scores,
        "metrics": metrics,
        "latency": latency,
        "debug": debug_info
    }

def compare_runs(result_A, result_B):
    """
    Quantify divergence between two pipeline runs.
    """

    retrieval_overlap = compute_overlap(
        result_A["retrieved_chunks"],
        result_B["retrieved_chunks"]
    )

    filtered_overlap = compute_overlap(
        result_A.get("filtered_context", []),
        result_B.get("filtered_context", [])
    )

    output_length_diff = abs(
        result_A["metrics"]["output_length"] -
        result_B["metrics"]["output_length"]
    )

    latency_diff = abs(
        result_A["metrics"]["total_latency"] -
        result_B["metrics"]["total_latency"]
    )

    return {
        "retrieval_overlap": retrieval_overlap,
        "filtered_overlap": filtered_overlap,
        "output_length_difference": output_length_diff,
        "latency_difference": round(latency_diff, 3)
    }
