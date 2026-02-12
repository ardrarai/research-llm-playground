import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
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


st.set_page_config(layout="wide")
st.title("Research LLM Pipeline Playground")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
query = st.text_input("Enter Research Question", "What research gaps exist?")
compare_mode = st.checkbox("Enable Side-by-Side Comparison Mode")

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------

st.sidebar.title("Pipeline Controls")
st.sidebar.markdown("### Chunk Strategy")

chunk_strategy = st.sidebar.radio(
    "Operating Mode",
    [
        "Precision (400)",
        "Balanced (600) Recommended",
        "Wide Context (800)",
        "Manual (400–800)"
    ],
    index=1
)

preset_map = {
    "Precision (400)": 400,
    "Balanced (600) Recommended": 600,
    "Wide Context (800)": 800
}

manual_chunk = st.sidebar.slider("Manual Chunk Size", 400, 800, 600)

def resolve_chunk_size():
    if chunk_strategy == "Manual (400–800)":
        return manual_chunk
    return preset_map[chunk_strategy]

# --------------------------------------------------
# CONFIG BUILDER
# --------------------------------------------------

def build_config(prefix="A"):

    st.sidebar.markdown(f"## Config {prefix}")

    chunk_size = resolve_chunk_size()

    chunk_overlap = st.sidebar.slider(
        f"Overlap {prefix}", 0, 300, 150, key=f"overlap_{prefix}"
    )

    retrieval_mode = st.sidebar.selectbox(
        f"Retrieval Mode {prefix}",
        ["dense", "bm25", "hybrid"],
        key=f"retrieval_{prefix}"
    )

    top_k = st.sidebar.slider(
        f"Top K {prefix}", 1, 10, 5, key=f"topk_{prefix}"
    )

    temperature = st.sidebar.slider(
        f"Temperature {prefix}", 0.0, 1.0, 0.2, key=f"temp_{prefix}"
    )

    prompt_mode = st.sidebar.selectbox(
        f"Prompt Mode {prefix}",
        ["conservative", "creative", "structured"],
        key=f"prompt_{prefix}"
    )

    return PipelineConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model="local",
        retrieval_mode=retrieval_mode,
        top_k=top_k,
        temperature=temperature,
        prompt_mode=prompt_mode
    )

config_A = build_config("A")
config_B = build_config("B") if compare_mode else None
run_button = st.button("Run Pipeline")

# --------------------------------------------------
# FILE SAVE
# --------------------------------------------------

def save_uploaded_file(uploaded_file):
    save_path = os.path.join("data", "uploads", uploaded_file.name)
    os.makedirs("data/uploads", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

# --------------------------------------------------
# MANUAL EXECUTION
# --------------------------------------------------

if run_button:

    if uploaded_file is None:
        st.error("Please upload a PDF first.")
        st.stop()

    save_path = save_uploaded_file(uploaded_file)

    if not compare_mode:

        with st.spinner("Running pipeline..."):
            result = run_pipeline(config_A, save_path, query)

        st.subheader("Generated Output")
        st.write(result["output"])

        st.subheader("Metrics")
        st.json(result["metrics"])

        log_single_run(config_A, result)

    else:

        with st.spinner("Running comparison..."):
            result_A = run_pipeline(config_A, save_path, query)
            result_B = run_pipeline(config_B, save_path, query)

        analysis = compare_runs(result_A, result_B)

        st.subheader("Divergence Analysis")
        st.json(analysis)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Config A")
            st.write(result_A["output"])
            st.json(result_A["metrics"])

        with col2:
            st.markdown("### Config B")
            st.write(result_B["output"])
            st.json(result_B["metrics"])

        log_comparison_run(config_A, result_A, config_B, result_B, analysis)

# --------------------------------------------------
# SWEEP
# --------------------------------------------------

st.markdown("---")
st.markdown("Automated Experiment Sweep")

run_sweep = st.button("Run Parameter Sweep")

if run_sweep:

    if uploaded_file is None:
        st.error("Upload PDF first.")
        st.stop()

    save_path = save_uploaded_file(uploaded_file)

    param_grid = {
        "chunk_size": [400, 600, 800],
        "top_k": [3, 5],
        "retrieval_mode": ["dense", "hybrid"]
    }

    configs = generate_config_grid(config_A, param_grid)

    progress_bar = st.progress(0)

    def progress_callback(current, total):
        progress_bar.progress(current / total)

    run_single_sweep(configs, save_path, query, progress_callback)
    st.success("Sweep completed and logged.")

# --------------------------------------------------
# HISTORY
# --------------------------------------------------

st.markdown("---")
st.markdown("Experiment History")

history = load_experiment_history()

if history:
    st.write(f"Total runs logged: {len(history)}")
else:
    st.info("No experiments logged yet.")

# --------------------------------------------------
# BEST CONFIG SELECTOR
# --------------------------------------------------

st.markdown("---")
st.markdown("Best Configuration Detector")

if history:
    best = select_best_config(history, objective="richness")

    if best:
        st.json(best)
    else:
        st.warning("No valid configurations yet.")

# --------------------------------------------------
# MODERN RADAR (Plotly)
# --------------------------------------------------

st.markdown("---")
st.markdown("Configuration Performance Radar")
st.caption("Top two configurations selected based on richness objective.")
st.caption("Higher surface area indicates stronger multi-dimensional research gap performance.")

if history:

    # Score runs properly using richness objective
    scored_runs = []

    for r in history:
        if r["mode"] == "single" and r["config"]["chunk_size"] in [400, 600, 800]:
            score_obj = select_best_config([r], objective="richness")
            if score_obj:
                scored_runs.append((r, score_obj["score"]))

    if len(scored_runs) >= 2:

        # Sort by computed richness score
        ranked = sorted(scored_runs, key=lambda x: x[1], reverse=True)

        best_run = ranked[0][0]
        second_run = ranked[1][0]

        fig = plot_comparison_radar(best_run, second_run, history)

        if fig:
            st.plotly_chart(fig, use_container_width=True)

