import plotly.graph_objects as go


def plot_comparison_radar(best_run, second_run, history):

    categories = [
        "Gap Density",
        "Filtered",
        "Retrieved",
        "Output",
        "Latency (Inv)"
    ]

    def extract(run):
        filtered = run["debug"]["filtered_sentence_count"]
        retrieved = run["metrics"]["retrieved_count"]
        output = run["metrics"]["output_length"]
        latency = run["metrics"]["total_latency"]

        density = filtered / retrieved if retrieved else 0
        inv_latency = 1 / latency if latency else 0

        return [density, filtered, retrieved, output, inv_latency]

    best_vals = extract(best_run)
    second_vals = extract(second_run)

    # Pairwise normalize
    norm_best = []
    norm_second = []

    for b, s in zip(best_vals, second_vals):
        min_v = min(b, s)
        max_v = max(b, s)

        if max_v == min_v:
            norm_best.append(0.5)
            norm_second.append(0.5)
        else:
            norm_best.append((b - min_v) / (max_v - min_v))
            norm_second.append((s - min_v) / (max_v - min_v))

    fig = go.Figure()

    # BEST CONFIG (strong, solid)
    fig.add_trace(go.Scatterpolar(
        r=norm_best + [norm_best[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Best Config',
        line=dict(color='#4CC9F0', width=3),
        fillcolor='rgba(76,201,240,0.35)',
    ))

    # SECOND CONFIG (dashed, lighter)
    fig.add_trace(go.Scatterpolar(
        r=norm_second + [norm_second[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Second Best',
        line=dict(color='#4361EE', width=2, dash='dash'),
        fillcolor='rgba(67,97,238,0.15)',
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='rgba(255,255,255,0.08)',
                linecolor='rgba(255,255,255,0.2)',
                tickfont=dict(size=9),
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                gridcolor='rgba(255,255,255,0.05)'
            )
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        width=480,
        height=480
    )

    return fig
