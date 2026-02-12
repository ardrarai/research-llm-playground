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

st.set_page_config(layout="wide")

st.title("🧪 Research LLM Pipeline Playground")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
query = st.text_input("Enter Research Question", "What research gaps exist?")

compare_mode = st.checkbox("Enable Side-by-Side Comparison Mode")

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------

st.sidebar.title("Pipeline Controls")

# --------------------------------------------------
# CHUNK SIZE CONTROL (RESEARCH-GRADE)
# --------------------------------------------------

st.sidebar.markdown("### Chunk Strategy")

chunk_strategy = st.sidebar.radio(
    "Operating Mode",
    [
        "Precision (400)",
        "Balanced (600) ⭐ Recommended",
        "Wide Context (800)",
        "Manual (400–800)"
    ],
    index=1
)

preset_map = {
    "Precision (400)": 400,
    "Balanced (600) ⭐ Recommended": 600,
    "Wide Context (800)": 800
}

manual_chunk = st.sidebar.slider(
    "Manual Chunk Size",
    400,
    800,
    600
)

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

# --------------------------------------------------
# BUILD CONFIGS
# --------------------------------------------------

config_A = build_config("A")
config_B = build_config("B") if compare_mode else None

run_button = st.button("Run Pipeline")

# --------------------------------------------------
# SWEEP UI
# --------------------------------------------------

st.markdown("---")
st.markdown("## 🔬 Automated Experiment Sweep")

run_sweep = st.button("Run Parameter Sweep (Batch Experiments)")

# --------------------------------------------------
# FILE SAVE HELPER
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

    # ---------- SINGLE ----------
    if not compare_mode:

        with st.spinner("Running pipeline..."):
            result = run_pipeline(config_A, save_path, query)

        st.subheader("📄 Generated Output")
        st.write(result["output"])

        st.subheader("📊 Metrics")
        st.json(result["metrics"])

        st.subheader("🧠 Filtered Gap Sentences")
        for s in result.get("filtered_context", []):
            st.write(f"- {s}")

        st.subheader("🔎 Retrieved Chunks")
        for i, (chunk, score) in enumerate(zip(result["retrieved_chunks"], result["scores"])):
            with st.expander(f"Chunk {i+1} | Score: {round(score,4)}"):
                st.write(chunk)

        log_single_run(config_A, result)

    # ---------- COMPARISON ----------
    else:

        with st.spinner("Running comparison..."):
            result_A = run_pipeline(config_A, save_path, query)
            result_B = run_pipeline(config_B, save_path, query)

        analysis = compare_runs(result_A, result_B)

        st.markdown("## 🧪 Divergence Analysis")
        st.json(analysis)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## 🅰 Config A Output")
            st.write(result_A["output"])
            st.markdown("### Metrics A")
            st.json(result_A["metrics"])

        with col2:
            st.markdown("## 🅱 Config B Output")
            st.write(result_B["output"])
            st.markdown("### Metrics B")
            st.json(result_B["metrics"])

        log_comparison_run(config_A, result_A, config_B, result_B, analysis)

# --------------------------------------------------
# SWEEP EXECUTION
# --------------------------------------------------

if run_sweep:

    if uploaded_file is None:
        st.error("Upload PDF first.")
        st.stop()

    save_path = save_uploaded_file(uploaded_file)

    st.info("Running automated experiments...")

    # Stable research sweep grid
    param_grid = {
        "chunk_size": [400, 600, 800],   # stable regime only
        "top_k": [3, 5],
        "retrieval_mode": ["dense", "hybrid"]
    }

    configs = generate_config_grid(config_A, param_grid)

    progress_bar = st.progress(0)
    status = st.empty()

    def progress_callback(current, total):
        progress_bar.progress(current / total)
        status.write(f"Running experiment {current} / {total}")

    run_single_sweep(
        configs,
        save_path,
        query,
        progress_callback
    )

    st.success(f"Completed {len(configs)} experiments and logged results.")

# --------------------------------------------------
# HISTORY VIEW
# --------------------------------------------------

st.markdown("---")
st.markdown("## 🧾 Experiment History")

history = load_experiment_history()

if history:
    st.write(f"Total runs logged: {len(history)}")

    for i, run in enumerate(reversed(history[-10:])):
        with st.expander(f"Run {len(history)-i} | {run['timestamp']} | {run['mode']}"):
            st.json(run)
else:
    st.info("No experiments logged yet.")
