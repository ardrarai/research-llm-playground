import re
import os
import pickle
import hashlib

from utils.pdf_loader import load_pdf

from pipeline.chunking.chunker import fixed_chunk_document
from pipeline.chunking.adaptive_chunker import adaptive_chunk_document

from pipeline.embedding.embedder import embed_chunks
from pipeline.retrieval.retriever import retrieve
from pipeline.generation.generator import generate_answer
from pipeline.evaluation.metrics import compute_metrics


# ---------------------------------------------------
# CACHE SETUP
# ---------------------------------------------------

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_key(text, config):
    return hashlib.md5(
        f"{len(text)}_{config.chunk_size}_{config.chunking_mode}".encode()
    ).hexdigest()


# ---------------------------------------------------
# GAP EXTRACTION
# ---------------------------------------------------

def extract_gap_sentences(chunks, max_sentences=12):

    keywords = [
        "limitation", "future", "lack", "gap",
        "uncertain", "not fully effective"
    ]

    results = []

    for chunk in chunks:
        sentences = re.split(r'(?<=[.!?])\s+', chunk)

        for s in sentences:
            if any(k in s.lower() for k in keywords):
                results.append(s.strip())

    return results[:max_sentences]


# ---------------------------------------------------
# CONTEXT CONTROL
# ---------------------------------------------------

def cap_context_length(sentences, max_chars=2500):

    combined = ""
    selected = []

    for s in sentences:
        if len(combined) + len(s) > max_chars:
            break
        combined += s + " "
        selected.append(s)

    return selected


# ---------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------

def run_pipeline(config, document_path, query):

    text = load_pdf(document_path)

    # ✅ CHUNKING SAFE
    if config.chunking_mode == "adaptive":
        chunks = adaptive_chunk_document(text)
    else:
        if config.chunk_size is None:
            raise ValueError("chunk_size cannot be None in fixed mode")

        chunks = fixed_chunk_document(
            text,
            config.chunk_size,
            config.chunk_overlap
        )

    # ⚡ CACHE EMBEDDINGS
    key = get_cache_key(text, config)
    path = os.path.join(CACHE_DIR, f"{key}.pkl")

    if os.path.exists(path):
        chunks, vectors = pickle.load(open(path, "rb"))
        embed_time = 0
    else:
        vectors, embed_time = embed_chunks(chunks, config.embedding_model)
        pickle.dump((chunks, vectors), open(path, "wb"))

    # RETRIEVE
    retrieved_chunks, scores = retrieve(
        query,
        vectors,
        chunks,
        config.retrieval_mode,
        config.top_k
    )

    # FILTER
    filtered = extract_gap_sentences(retrieved_chunks)

    # CONTEXT
    if filtered:
        context = cap_context_length(filtered)
    else:
        context = cap_context_length(retrieved_chunks[:3])

    # GENERATE
    output, gen_time = generate_answer(
        query,
        context,
        config.temperature,
        config.prompt_mode
    )

    latency = {
        "embedding_time": embed_time,
        "generation_time": gen_time
    }

    metrics = compute_metrics(retrieved_chunks, output, latency)

    debug = {
        "chunking_mode": config.chunking_mode,
        "total_chunks_created": len(chunks),
        "retrieved_count": len(retrieved_chunks),
        "filtered_sentence_count": len(filtered),
        "context_sentences_used": len(context)
    }

    return {
        "output": output,
        "retrieved_chunks": retrieved_chunks,
        "filtered_context": filtered,
        "scores": scores,
        "metrics": metrics,
        "latency": latency,
        "debug": debug
    }


# ---------------------------------------------------
# COMPARISON
# ---------------------------------------------------

def compute_overlap(a, b):
    if not a and not b:
        return 1.0
    return round(len(set(a) & set(b)) / len(set(a) | set(b)), 3)


def compare_runs(A, B):

    return {
        "retrieval_overlap": compute_overlap(A["retrieved_chunks"], B["retrieved_chunks"]),
        "filtered_overlap": compute_overlap(A["filtered_context"], B["filtered_context"]),
        "output_length_difference": abs(A["metrics"]["output_length"] - B["metrics"]["output_length"]),
        "latency_difference": round(abs(A["metrics"]["total_latency"] - B["metrics"]["total_latency"]), 3)
    }
