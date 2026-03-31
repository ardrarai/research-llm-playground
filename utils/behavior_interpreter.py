def interpret_metrics(result):

    insights = []

    signals = result["debug"]["filtered_sentence_count"]
    latency = result["metrics"]["total_latency"]
    output_len = result["metrics"]["output_length"]

    if signals <= 3:
        insights.append("Low signal extraction → weak contextual grounding")

    if signals >= 8:
        insights.append("Strong signal extraction → rich context provided")

    if latency > 50:
        insights.append("High latency → large context or complex reasoning")

    if output_len > 1200:
        insights.append("Broad output → high exploration")

    if output_len < 800:
        insights.append("Concise output → focused reasoning")

    return insights


def detect_failure_modes(config, result):

    failures = []

    if config.chunk_size and config.chunk_size <= 400:
        failures.append("Fragmented context (small chunks).")

    if config.chunk_size and config.chunk_size >= 800:
        failures.append("Diluted context (large chunks).")

    if result["debug"].get("filtered_sentence_count", 0) == 0:
        failures.append("No signals extracted.")

    return failures

