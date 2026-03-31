import sys
import os

# Ensure imports work on Streamlit Cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from utils.behavior_interpreter import interpret_metrics, detect_failure_modes
from utils.timeline_visualizer import (
    plot_experiment_timeline,
    generate_timeline_insights
)
from pipeline.orchestrator import run_pipeline, compare_runs
from utils.config_schema import PipelineConfig
from utils.experiment_logger import (
    log_single_run,
    log_comparison_run,
    load_experiment_history
)
from utils.experiment_sweeper import (
    generate_config_grid,
    run_single_sweep
)
from utils.best_config_selector import select_best_config
from utils.radar_visualizer import plot_comparison_radar


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="LLM Pipeline Behavior System",
    layout="wide"
)

st.title("LLM Pipeline Behavior Analysis System")
st.caption("Controlled experimental environment for studying how RAG configurations influence LLM behavior")

st.markdown("""
### System Purpose

This interface exposes how structural pipeline decisions affect:

- reasoning coherence
- retrieval quality
- latency and context utilization

The system is designed for **observation, not optimization**.
""")

st.info("Outputs may vary across identical runs due to inherent variability in generative systems.")


# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

st.markdown("---")
st.header("Experiment Setup")

uploaded_file = st.file_uploader("Upload Research Document (PDF)", type="pdf")

query = st.text_input(
    "Research Question",
    "What research gaps exist?"
)

experiment_note = st.text_input(
    "Experiment Intent",
    placeholder="What are you testing?"
)

col1, col2 = st.columns([2, 1])

with col1:
    experiment_mode = st.radio(
        "Experiment Mode",
        ["Single Run", "Batch Study"]
    )

with col2:
    compare_mode = st.checkbox("Enable Configuration Comparison")


# --------------------------------------------------
# SIDEBAR CONFIGURATION
# --------------------------------------------------

st.sidebar.title("Pipeline Controls")

st.sidebar.markdown("### Semantic Segmentation")
st.sidebar.caption("Controls coherence vs fragmentation")

chunking_mode = st.sidebar.radio(
    "Segmentation Strategy",
    ["Fixed", "Adaptive"]
)


def resolve_chunking_mode():
    return "adaptive" if chunking_mode == "Adaptive" else "fixed"


def resolve_chunk_size():
    if resolve_chunking_mode() == "adaptive":
        return None

    mode = st.sidebar.radio(
        "Chunk Size",
        ["400", "600", "800", "Manual"]
    )

    if mode == "Manual":
        return st.sidebar.slider("Manual Size", 400, 800, 600)

    return int(mode)


def build_config(prefix="A"):

    chunk_size = resolve_chunk_size()

    if resolve_chunking_mode() == "fixed":
        chunk_overlap = st.sidebar.slider(f"Overlap {prefix}", 0, 300, 150)
    else:
        chunk_overlap = 0

    st.sidebar.markdown("---")

    retrieval_mode = st.sidebar.selectbox(
        f"Retrieval Strategy {prefix}",
        ["dense", "bm25", "hybrid"]
    )

    top_k = st.sidebar.slider(f"Top-K {prefix}", 1, 10, 5)
    temperature = st.sidebar.slider(f"Temperature {prefix}", 0.0, 1.0, 0.2)

    prompt_mode = st.sidebar.selectbox(
        f"Prompt Mode {prefix}",
        ["conservative", "creative", "structured"]
    )

    return PipelineConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model="local",
        retrieval_mode=retrieval_mode,
        top_k=top_k,
        temperature=temperature,
        prompt_mode=prompt_mode,
        chunking_mode=resolve_chunking_mode()
    )


config_A = build_config("A")
config_B = build_config("B") if compare_mode else None


# --------------------------------------------------
# FILE HANDLING
# --------------------------------------------------

def save_file(file):
    path = os.path.join("data", "uploads", file.name)
    os.makedirs("data/uploads", exist_ok=True)
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    return path


# --------------------------------------------------
# RUN EXECUTION
# --------------------------------------------------

st.markdown("---")
run_button = st.button("Run Experiment", use_container_width=True)

if run_button:

    if uploaded_file is None:
        st.error("Please upload a PDF before running the experiment.")
        st.stop()

    try:
        path = save_file(uploaded_file)

        if experiment_mode == "Single Run":

            result = run_pipeline(config_A, path, query)

            st.markdown("## Observability Metrics")

            c1, c2, c3 = st.columns(3)
            c1.metric("Chunks", result["debug"]["total_chunks_created"])
            c2.metric("Signals", result["debug"]["filtered_sentence_count"])
            c3.metric("Latency (s)", round(result["metrics"]["total_latency"], 2))

            st.caption("Metrics reflect how configuration influences system behavior")

            st.markdown("## Interpretation")

            if experiment_note:
                st.info(f"Intent: {experiment_note}")

            for insight in interpret_metrics(result):
                st.write(f"- {insight}")

            failures = detect_failure_modes(config_A, result)
            for f in failures:
                st.error(f)

            with st.expander("Generated Output"):
                st.write(result["output"])

            log_single_run(config_A, result)

        else:
            st.warning("Batch mode execution configured. (Ensure sweep logic is implemented)")

    except Exception as e:
        st.error(f"Execution failed: {str(e)}")


# --------------------------------------------------
# COMPARISON RADAR
# --------------------------------------------------

history = load_experiment_history()

if history:

    valid_runs = [r for r in history if r["mode"] == "single"]

    if len(valid_runs) >= 2:

        st.markdown("---")
        st.header("Configuration Comparison")

        st.caption("Compares how different configurations affect system behavior")

        ranked = sorted(
            valid_runs,
            key=lambda r: r["debug"]["filtered_sentence_count"],
            reverse=True
        )

        best_run = ranked[0]
        second_run = ranked[1]

        fig = plot_comparison_radar(best_run, second_run, history)

        if fig:
            st.plotly_chart(fig, use_container_width=False)


# --------------------------------------------------
# TIMELINE + INSIGHTS
# --------------------------------------------------

if history:

    st.markdown("---")
    st.header("Experiment Evolution")

    st.caption("Each point represents configuration → behavior mapping")

    fig = plot_experiment_timeline(history)

    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## Causal Insights")

    insights = generate_timeline_insights(history)

    for insight in insights:
        st.success(insight)


# --------------------------------------------------
# BEST CONFIG
# --------------------------------------------------

if history:

    st.markdown("---")
    st.header("Best Configuration (Observed)")

    best = select_best_config(history, objective="richness")

    if best:
        st.json(best)
