import faiss
import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def dense_retrieve(query_vector, vectors, chunks, top_k, lambda_param=0.7):
    """
    Dense retrieval with MMR for diversity.
    """

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    D, I = index.search(np.array([query_vector]), len(chunks))

    similarities = [1 / (1 + d) for d in D[0]]

    selected = []
    selected_scores = []
    selected_indices = []

    for _ in range(top_k):
        best_score = -1
        best_idx = -1

        for i, idx in enumerate(I[0]):
            if idx in selected_indices:
                continue

            relevance = similarities[i]

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

        selected_indices.append(best_idx)
        selected.append(chunks[best_idx])
        selected_scores.append(best_score)

    return selected, selected_scores
