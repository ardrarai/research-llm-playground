def hybrid_retrieve(query, query_vector, vectors, chunks, top_k, dense_func, bm25_func):
    """
    Hybrid retrieval using score fusion.
    """

    dense_results, dense_scores = dense_func(query_vector, vectors, chunks, top_k)
    bm25_results, bm25_scores = bm25_func(query, chunks, top_k)

    score_dict = {}

    # Add dense scores
    for chunk, score in zip(dense_results, dense_scores):
        score_dict[chunk] = score_dict.get(chunk, 0) + score

    # Add BM25 scores
    for chunk, score in zip(bm25_results, bm25_scores):
        score_dict[chunk] = score_dict.get(chunk, 0) + score

    ranked = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    results = [item[0] for item in ranked[:top_k]]
    scores = [item[1] for item in ranked[:top_k]]

    return results, scores
