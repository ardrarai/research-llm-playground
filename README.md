# LLM Pipeline Behavior Analysis System
**Status:** Experimental Research System

---

## 1. Problem

Most LLM-based systems are tuned through prompt engineering, while upstream pipeline decisions remain fixed and largely unexamined. This leads to unstable outputs, weak interpretability, and difficulty in diagnosing failure modes.

In practice, generation quality is often treated as a property of the model, when it is significantly influenced by pipeline structure.

This system treats a Retrieval-Augmented Generation (RAG) pipeline as a **controllable system**, where behavior is studied through structured variation of configuration parameters.

The objective is to answer:

> Which parts of the pipeline actually control reasoning behavior and output quality?

---

## 2. System Structure

Pipeline:
PDF → Chunking → Embedding → Retrieval → Context Filtering → Generation → Logging

Each stage is explicitly configurable and observable.

---

## 3. What the System Enables

- Controlled variation of pipeline parameters
- Side-by-side comparison of configurations
- Parameter sweeps across defined ranges
- Logging of system-level behavior

The system is not optimized for output quality alone.
It is designed to observe **how outputs change under controlled conditions**.

---

## 4. Experimental Variables

| Variable | Description | Expected Effect |
|----------|------------|----------------|
| Chunk Size | Token length of text segments | Coherence vs fragmentation |
| Retrieval Strategy | Dense / Hybrid (dense + lexical) | Precision vs recall |
| Retrieval Depth (Top-K) | Number of retrieved chunks | Reasoning breadth vs latency |
| Context Filtering | Signal-based filtering | Noise reduction vs coverage |

Each experiment isolates one variable while holding others constant.

---

## 5. Observability

Each run logs:

- retrieval statistics
- filtered context density
- output length
- latency breakdown
- context utilization

These logs allow reproducible comparison across configurations.

---

## 6. Experiment Log (Representative Runs)

### 6.1 Chunk Size Sensitivity

| Chunk Size | Observed Behavior | Output Quality | Latency |
|------------|-----------------|----------------|---------|
| ~400 tokens | Fragmented context, incoherent reasoning | Low | Low |
| ~600 tokens | Balanced context, consistent reasoning | High | Moderate |
| ≥800 tokens | Context dilution, reduced specificity | Medium | High |

**Observation:**
Chunk size acts as a primary control parameter for reasoning behavior.

---

### 6.2 Retrieval Strategy Comparison

| Strategy | Precision | Recall | Output Behavior |
|----------|----------|--------|-----------------|
| Dense | High | Lower | Focused, narrow reasoning |
| Hybrid | Moderate | High | Broader, exploratory reasoning |

**Observation:**
Hybrid retrieval increases coverage but introduces noise.

---

### 6.3 Retrieval Depth (Top-K)

| Top-K | Context Size | Reasoning Breadth | Latency |
|------|-------------|------------------|---------|
| 1–3 | Low | Narrow | Low |
| 5–8 | Moderate | Balanced | Moderate |
| 10+ | High | Broad but noisy | High |

**Observation:**
Retrieval depth directly controls reasoning complexity and latency.

---

### 6.4 Stability Check (Repeated Runs)

| Configuration | Run Variability | Notes |
|--------------|----------------|------|
| Fixed config (chunk=600, k=5) | Moderate | Output phrasing varies |
| Hybrid + high k | High | Redundancy and drift observed |

**Observation:**
Outputs are not deterministic even under identical configurations.

---

## 7. Key Findings

- Chunking determines reasoning coherence more than model choice
- Retrieval strategy controls conceptual breadth
- Retrieval depth scales reasoning complexity and latency
- Output stability is inherently variable

---

## 8. Failure Modes

- Over-fragmentation at small chunk sizes
- Redundant context at high retrieval depth
- Loss of specificity at large chunk sizes
- Instability across repeated runs

These are treated as system properties, not bugs.

---

## 9. Interface

The system includes a minimal Streamlit interface supporting:

- manual configuration runs
- side-by-side comparison
- parameter sweeps

The interface is intentionally simple. The focus is on behavior, not presentation.

---

## 10. Setup

Install dependencies:

```bash
pip install -r requirements.txt
```
Run the system:
```bash
streamlit run app.py
```
---

## 11. Design Philosophy
Control over creativity
Observability over output quality
Experimentation over assumptions
Stability and failure are first-class concerns

---

## 12. Limitations
| Area          | Limitation                      |
| ------------- | ------------------------------- |
| Chunking      | Fixed-size segmentation         |
| Filtering     | Heuristic signal detection      |
| Evaluation    | No statistical validation       |
| Scope         | Limited multi-document analysis |
| Deduplication | No semantic redundancy removal  |

---

## 13. Purpose

This system is not designed to produce answers.

It is designed to make LLM behavior observable, controllable, and analyzable.

