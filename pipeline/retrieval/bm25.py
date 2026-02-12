from rank_bm25 import BM25Okapi

def bm25_retrieve(query, chunks, top_k):
    tokenized_chunks = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)

    scores = bm25.get_scores(query.split())
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

    top_indices = ranked[:top_k]
    results = [chunks[i] for i in top_indices]
    top_scores = [scores[i] for i in top_indices]

    return results, top_scores
