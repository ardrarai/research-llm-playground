import plotly.graph_objects as go


def plot_experiment_timeline(history):

    runs = [r for r in history if r["mode"] == "single"]

    if len(runs) < 2:
        return None

    x = list(range(len(runs)))

    signals = [r["debug"]["filtered_sentence_count"] for r in runs]
    latency = [r["metrics"]["total_latency"] for r in runs]
    output_len = [r["metrics"]["output_length"] for r in runs]
    configs = [r["config"] for r in runs]

    fig = go.Figure()

    # ---------------- MAIN LINES ----------------
    fig.add_trace(go.Scatter(
        x=x,
        y=signals,
        mode='lines+markers',
        name='Signal'
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=latency,
        mode='lines+markers',
        name='Latency'
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=output_len,
        mode='lines+markers',
        name='Output'
    ))

    # ---------------- CAUSAL MARKERS ----------------
    annotations = []

    for i in range(1, len(configs)):
        prev = configs[i - 1]
        curr = configs[i]

        change = None

        if prev["retrieval_mode"] != curr["retrieval_mode"]:
            change = f"Retrieval: {prev['retrieval_mode']} → {curr['retrieval_mode']}"

        elif prev.get("chunk_size") != curr.get("chunk_size"):
            change = f"Chunk: {prev.get('chunk_size')} → {curr.get('chunk_size')}"

        if change:
            annotations.append(
                dict(
                    x=i,
                    y=signals[i],
                    text=change,
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40,
                    font=dict(size=10)
                )
            )

    fig.update_layout(
        title="Experiment Evolution (with Behavioral Triggers)",
        xaxis_title="Experiment Index",
        yaxis_title="Metric Value",
        template="plotly_dark",
        height=500,
        annotations=annotations
    )

    return fig


# --------------------------------------------------
# 🧠 CLEANED + SMART INSIGHTS
# --------------------------------------------------

def generate_timeline_insights(history):

    runs = [r for r in history if r["mode"] == "single"]

    if len(runs) < 3:
        return ["Not enough experiments to infer behavioral patterns"]

    signals = [r["debug"]["filtered_sentence_count"] for r in runs]
    latency = [r["metrics"]["total_latency"] for r in runs]
    output_len = [r["metrics"]["output_length"] for r in runs]
    configs = [r["config"] for r in runs]

    insights = []

    # ---------------- VARIABILITY ----------------
    if max(signals) - min(signals) > 3:
        insights.append("System highly sensitive → small config changes causing large signal variation")

    if max(latency) > 2 * min(latency):
        insights.append("Latency unstable → context size strongly affects generation cost")

    # ---------------- TREND ----------------
    if signals[-1] > signals[0]:
        insights.append("Signal quality improving across experiments → tuning is effective")

    if output_len[-1] < output_len[0]:
        insights.append("Outputs becoming more concise → potential increase in precision")

    # ---------------- COMPRESSED CAUSAL INSIGHTS ----------------
    retrieval_changes = set()
    chunk_changes = set()

    for i in range(1, len(configs)):
        prev = configs[i - 1]
        curr = configs[i]

        if prev["retrieval_mode"] != curr["retrieval_mode"]:
            retrieval_changes.add((prev["retrieval_mode"], curr["retrieval_mode"]))

        if prev.get("chunk_size") != curr.get("chunk_size"):
            chunk_changes.add((prev.get("chunk_size"), curr.get("chunk_size")))

    if retrieval_changes:
        insights.append(
            f"Retrieval strategy shifts observed: {len(retrieval_changes)} distinct transitions"
        )

    if chunk_changes:
        insights.append(
            f"Chunk size variations detected across configurations ({len(chunk_changes)} patterns)"
        )

    # ---------------- FAILURE PATTERN ----------------
    if sum(1 for s in signals if s <= 3) > len(signals) // 2:
        insights.append("Frequent weak signals → segmentation or retrieval misconfigured")

    if not insights:
        insights.append("System behavior stable with no strong patterns")

    return insights
