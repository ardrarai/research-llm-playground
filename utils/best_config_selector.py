import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# ----------------------------
# Normalization
# ----------------------------

def normalize(values):
    if not values:
        return []

    min_v = min(values)
    max_v = max(values)

    if max_v == min_v:
        return [0.5 for _ in values]

    return [(v - min_v) / (max_v - min_v) for v in values]


# ----------------------------
# Global embedding model
# ----------------------------

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ----------------------------
# Diversity computation
# ----------------------------

def compute_diversity(sentences):
    """
    Computes semantic diversity score between 0 and 1.
    Higher = more diverse.
    """

    if not sentences or len(sentences) < 2:
        return 0.5  # neutral

    model = get_model()
    embeddings = model.encode(sentences)

    sim_matrix = cosine_similarity(embeddings)

    sims = []

    for i in range(len(sim_matrix)):
        for j in range(i + 1, len(sim_matrix)):
            sims.append(sim_matrix[i][j])

    if not sims:
        return 0.5

    avg_similarity = np.mean(sims)

    diversity = 1 - avg_similarity

    return float(diversity)


# ----------------------------
# Best Config Selector
# ----------------------------

def select_best_config(history, objective="balanced"):

    single_runs = [r for r in history if r["mode"] == "single"]

    if not single_runs:
        return None

    # Only stable regime
    stable_runs = [
        r for r in single_runs
        if r["config"]["chunk_size"] in [400, 600, 800]
    ]

    if not stable_runs:
        return None

    filtered_counts = [
        r["debug"]["filtered_sentence_count"]
        for r in stable_runs
    ]

    retrieved_counts = [
        r["metrics"]["retrieved_count"]
        for r in stable_runs
    ]

    output_lengths = [
        r["metrics"]["output_length"]
        for r in stable_runs
    ]

    latencies = [
        r["metrics"]["total_latency"]
        for r in stable_runs
    ]

    # Gap density
    gap_density = [
        (filtered_counts[i] / retrieved_counts[i])
        if retrieved_counts[i] > 0 else 0
        for i in range(len(stable_runs))
    ]

    # Diversity
    diversity_scores = [
        compute_diversity(r.get("filtered_context", []))
        for r in stable_runs
    ]

    # Normalize everything
    norm_density = normalize(gap_density)
    norm_filtered = normalize(filtered_counts)
    norm_retrieved = normalize(retrieved_counts)
    norm_output = normalize(output_lengths)
    norm_latency = normalize(latencies)
    norm_diversity = normalize(diversity_scores)

    scored = []

    for i, run in enumerate(stable_runs):

        if objective == "richness":

            score = (
                0.35 * norm_density[i]
                + 0.20 * norm_filtered[i]
                + 0.15 * norm_retrieved[i]
                + 0.15 * norm_diversity[i]
                + 0.10 * norm_output[i]
                - 0.05 * norm_latency[i]
            )

        else:  # balanced

            score = (
                0.35 * norm_filtered[i]
                + 0.2 * norm_output[i]
                + 0.15 * norm_retrieved[i]
                - 0.3 * norm_latency[i]
            )

        scored.append((run, score))

    if not scored:
        return None

    scored.sort(key=lambda x: x[1], reverse=True)

    best_run, best_score = scored[0]

    return {
        "objective": objective,
        "score": round(best_score, 4),
        "config": best_run["config"],
        "metrics": best_run["metrics"],
        "debug": best_run["debug"]
    }
