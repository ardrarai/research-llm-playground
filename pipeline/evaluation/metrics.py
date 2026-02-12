def compute_metrics(retrieved_chunks, output, latency_data):

    if len(retrieved_chunks) > 0:
        avg_chunk_length = sum(len(c) for c in retrieved_chunks) / len(retrieved_chunks)
    else:
        avg_chunk_length = 0

    metrics = {
        "retrieved_count": len(retrieved_chunks),
        "avg_chunk_length": round(avg_chunk_length, 2),
        "output_length": len(output),
        "embedding_time": latency_data.get("embedding_time", 0),
        "generation_time": latency_data.get("generation_time", 0),
        "total_latency": round(sum(latency_data.values()), 4)
    }

    return metrics
