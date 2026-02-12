from .dense import dense_retrieve
from .bm25 import bm25_retrieve
from .hybrid import hybrid_retrieve
from pipeline.embedding.local_embedding import embed_local

def retrieve(query, vectors, chunks, mode, top_k):

    if mode == "dense":
        query_vector = embed_local([query])[0]
        return dense_retrieve(query_vector, vectors, chunks, top_k)

    elif mode == "bm25":
        return bm25_retrieve(query, chunks, top_k)

    elif mode == "hybrid":
        query_vector = embed_local([query])[0]
        return hybrid_retrieve(
            query,
            query_vector,
            vectors,
            chunks,
            top_k,
            dense_retrieve,
            bm25_retrieve
        )

    else:
        raise ValueError("Invalid retrieval mode")
