# Research Gap Extraction Pipeline (RAG-Based) — v1

## Overview

This project is an experimental research pipeline for extracting **latent research gaps** from academic PDFs using a configurable Retrieval-Augmented Generation (RAG) architecture.

The system was built to investigate a practical problem:
> Existing LLM summarization tools generate generic “future work” statements but fail to extract context-grounded, evidence-driven research gaps from real literature.

This pipeline addresses that limitation by explicitly structuring:
1. semantic segmentation
2. retrieval strategy
3. gap-signal filtering
4. context-conditioned generation
and measuring how pipeline configuration affects gap quality.

The system is designed not only as a utility, but as an **experimental environment for studying RAG behavior under controlled parameter variation**.

---

## Core Pipeline Architecture
PDF → Chunking → Embedding → Retrieval → Gap Signal Filtering → Generation → Evaluation

### Components

**Document Loader**
- Extracts raw text from PDF

**Semantic Chunker**
- Fixed-size sliding window segmentation
- Overlap-based continuity preservation

**Embedding Layer**
- Local embedding model
- Vector representation for semantic retrieval

**Retrieval Engine**
Supports three modes:
- Dense vector similarity
- BM25 lexical retrieval
- Hybrid fusion retrieval

**Gap Signal Extractor**
Heuristic sentence filter detecting research-gap indicators such as:
- limitation
- lack of evidence
- requires further investigation
- heterogeneity
- unclear outcomes
- not widely adopted
- future research needed

**Context-Aware Generator**
LLM conditioned only on filtered gap-relevant sentences when available.

**Evaluation Module**
Computes:
- retrieved context statistics
- generation length
- latency components
- chunk distribution
- context utilization density

---

## Interactive Experiment Interface
Streamlit interface supports:

### Single Run Mode
Run pipeline with manual parameter configuration.

### Side-by-Side Comparison Mode
Parallel execution of two configurations with divergence metrics:
- retrieval overlap
- filtered context overlap
- output length difference
- latency difference

### Automated Parameter Sweep
Batch experiment runner across configurable parameter grids.
All runs are automatically logged.

---

## Experiment Logging

Every execution records:
- full configuration
- retrieval statistics
- generation metrics
- chunk distribution
- context utilization
- divergence analysis (for comparisons)

This enables longitudinal performance tracking and configuration sensitivity analysis.

---

## Empirical Research Findings (v1)

Experiments were conducted across multiple configurations varying:
- chunk size
- retrieval strategy
- retrieval depth (top-k)
All findings below are derived from recorded pipeline runs.

---

### 1. Chunk Size is a First-Order Control Parameter

Chunk size directly determines:
- semantic coherence of retrieval units
- retrieval search space size
- context signal density
- generation specificity
- overall latency

Observed behavior:

| Chunk Size | Effect |
|---|---|
| Small chunks (≈400) | semantic fragmentation, noisy retrieval, low signal density |
| Medium chunks (≈600) | optimal semantic coherence and retrieval precision |
| Large chunks (≈800+) | context dilution and reduced gap specificity |

Empirically optimal range: ~100–140 chunks per document

For the tested corpus, this corresponded to: chunk_size ≈ 600

---

### 2. Retrieval Strategy Controls Conceptual Breadth

Dense retrieval:
- higher precision
- fewer gap signals
- shorter outputs
- lower generation cost

Hybrid retrieval:
- higher recall
- more extracted gap statements
- longer reasoning chains
- increased generation latency

Interpretation:
dense → precision-oriented gap extraction
hybrid → exploratory gap discovery

### 3. Retrieval Depth Governs Reasoning Complexity

Increasing `top_k` produces:
- higher context sentence count
- increased conceptual diversity
- longer generated outputs
- increased inference time
Retrieval depth acts as a direct control over reasoning breadth.

---

### 4. Generation Latency is Context-Driven

Latency is dominated by: generation_time >> embedding_time
Inference cost scales with:
- number of filtered sentences
- semantic density of context
- retrieval recall (hybrid > dense)
Embedding and chunking have secondary impact.

---

### 5. Optimal Operational Configurations

**Balanced precision-performance**
chunk_size = 600
retrieval_mode = dense
top_k = 5

**Maximum research discovery**
chunk_size = 600
retrieval_mode = hybrid
top_k = 5

**Fast baseline execution**
chunk_size = 800
retrieval_mode = dense
top_k = 3

---

## System Design Insight
This project demonstrates that RAG pipelines are highly sensitive to **semantic segmentation structure**, not only retrieval method.
Chunking is not preprocessing — it is a primary model behavior control mechanism.
This has direct implications for:
- research synthesis systems
- automated literature reviews
- evidence gap mapping
- scientific discovery tooling

---

## Current Limitations
- heuristic gap detection (keyword-driven)
- fixed chunk sizing (non-adaptive)
- no statistical significance testing
- single-document processing
- no semantic deduplication of gaps

---

## Version v1 Scope
Version 1 establishes:
- stable modular RAG pipeline
- configuration comparison framework
- experiment logging infrastructure
- empirical parameter sensitivity analysis
- reproducible performance observations
This version serves as the baseline experimental platform.

---

## Next Research Directions
Planned investigation areas:
- adaptive chunk size calibration
- semantic gap clustering
- cross-document gap aggregation
- retrieval confidence scoring
- automatic configuration optimization

---

## Purpose
This system was developed to solve a practical analytical problem:
extracting meaningful, context-grounded research gaps from real academic literature — not generating generic future work statements.
The project functions both as a research tool and as an experimental environment for studying structured RAG behavior.

---

## Version
---

## System Design Insight

This project demonstrates that RAG pipelines are highly sensitive to **semantic segmentation structure**, not only retrieval method.

Chunking is not preprocessing — it is a primary model behavior control mechanism.

This has direct implications for:

- research synthesis systems
- automated literature reviews
- evidence gap mapping
- scientific discovery tooling

---

## Current Limitations

- heuristic gap detection (keyword-driven)
- fixed chunk sizing (non-adaptive)
- no statistical significance testing
- single-document processing
- no semantic deduplication of gaps

---

## Version v1 Scope

Version 1 establishes:

- stable modular RAG pipeline
- configuration comparison framework
- experiment logging infrastructure
- empirical parameter sensitivity analysis
- reproducible performance observations

This version serves as the baseline experimental platform.

---

## Next Research Directions

Planned investigation areas:

- adaptive chunk size calibration
- semantic gap clustering
- cross-document gap aggregation
- retrieval confidence scoring
- automatic configuration optimization

---

## Purpose

This system was developed to solve a practical analytical problem:

extracting meaningful, context-grounded research gaps from real academic literature — not generating generic future work statements.

The project functions both as a research tool and as an experimental environment for studying structured RAG behavior.

---

## Version
v1 — Baseline experimental release

---
