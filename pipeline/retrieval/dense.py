import numpy as np

# --------------------------------------------
# OPTIONAL FAISS IMPORT (SAFE)
# --------------------------------------------
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


# --------------------------------------------
# UTILS
# --------------------------------------------

def cosine_similarity(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return np.dot(a, b) / denom


def compute_similarity_scores(query_vector, vectors):
    """
    Fallback similarity computation using cosine similarity
    """
    sims = []
    for vec in vectors:
        sims.append(cosine_similarity(query_vector, vec))
    return np.array(sims)


# --------------------------------------------
# MAIN RETRIEVER
# --------------------------------------------

def dense_retrieve(query_vector, vectors, chunks, top_k, lambda_param=0.7):
    """
    Dense retrieval with MMR (Maximal Marginal Relevance)

    Works with:
    - FAISS (if available)
    - Numpy fallback (deployment-safe)
    """

    # --------------------------------------------
    # STEP 1: GET SIMILARITY SCORES
    # --------------------------------------------

    if FAISS_AVAILABLE:
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)

        D, I = index.search(np.array([query_vector]), len(chunks))

        # Convert L2 distance → similarity
        similarities = np.array([1 / (1 + d) for d in D[0]])
        candidate_indices = I[0]

    else:
        # Fallback path (used in Streamlit Cloud)
        similarities = compute_similarity_scores(query_vector, vectors)
        candidate_indices = np.argsort(similarities)[::-1]  # descending


    # --------------------------------------------
    # STEP 2: MMR SELECTION
    # --------------------------------------------

    selected = []
    selected_scores = []
    selected_indices = []

    for _ in range(min(top_k, len(chunks))):

        best_score = -1
        best_idx = -1

        for idx in candidate_indices:

            if idx in selected_indices:
                continue

            relevance = similarities[idx]

            diversity_penalty = 0
            for sel_idx in selected_indices:
                diversity_penalty = max(
                    diversity_penalty,
                    cosine_similarity(vectors[idx], vectors[sel_idx])
                )

            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity_penalty

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        if best_idx == -1:
            break

        selected_indices.append(best_idx)
        selected.append(chunks[best_idx])
        selected_scores.append(best_score)

    return selected, selected_scores
