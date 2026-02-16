# Research Gap Extraction Pipeline (RAG-Based)
**Version:** v2
**Status:** Experimental Research System
---
## Overview
This project is a configurable Retrieval-Augmented Generation (RAG) pipeline designed to **extract context-grounded research gaps from academic PDFs**.
The motivation is simple but unresolved in most tooling:
> Existing LLM-based summarization systems produce generic “future work” statements but fail to surface evidence-backed, literature-specific research gaps.
This pipeline treats *research gap extraction* as a **controlled systems problem**, not a prompt engineering task.
It explicitly studies how RAG configuration choices influence the **quality, density, and diversity** of extracted gaps.
---
## System Architecture
**PDF → Chunking → Embedding → Retrieval → Gap Filtering → Generation → Evaluation**
### Core Components
- **PDF Loader**
  Extracts raw text from academic PDFs.
- **Semantic Chunker**
  Fixed-size sliding window segmentation with overlap to preserve semantic continuity.
- **Embedding Layer**
  Local embedding model for semantic similarity search.
- **Retrieval Engine**
  Supports:
  - Dense vector retrieval
  - BM25 lexical retrieval
  - Hybrid (dense + lexical fusion)
- **Gap Signal Filter**
  Heuristic sentence-level filter targeting gap indicators such as:
  limitations, lack of evidence, unresolved issues, unclear outcomes, low adoption, and future research needs.
- **Context-Aware Generator**
  Conditions the LLM **only on gap-relevant sentences** when available, avoiding generic synthesis.
- **Evaluation Module**
  Logs:
  - retrieved context statistics
  - filtered sentence density
  - generation length
  - latency breakdown
  - context utilization
---
## Interactive Experiment Interface
The Streamlit interface supports:
### Single Run Mode
Manual configuration and execution of the pipeline.
### Side-by-Side Comparison Mode
Parallel execution of two configurations with divergence analysis:
- retrieval overlap
- filtered context overlap
- output length difference
- latency difference
### Automated Parameter Sweep
Batch execution across parameter grids with full experiment logging.
---
## Experiment Logging
Every run records:
- full configuration
- retrieval statistics
- filtered gap counts
- latency metrics
- context utilization
- comparison divergence (when applicable)
This enables **configuration sensitivity analysis and reproducible experimentation**.
---
## Empirical Findings (v1–v2)
All observations below are derived from logged experiments.
### Chunk Size Is a First-Order Control Parameter
Chunk size directly affects:
- semantic coherence
- retrieval precision
- gap signal density
- generation specificity
- inference latency
Observed behavior:
| Chunk Size | Outcome |
|----------|--------|
| ~400 | Fragmented context, noisy gaps |
| ~600 | Optimal balance of coherence and precision |
| ≥800 | Context dilution, reduced gap specificity |
**Empirically optimal regime:** ~600 tokens per chunk.
---
### Retrieval Strategy Controls Conceptual Breadth
- **Dense retrieval**
  Higher precision, fewer gaps, faster inference.
- **Hybrid retrieval**
  Higher recall, richer gap discovery, higher latency.
Interpretation:
Dense → precision-oriented extraction
Hybrid → exploratory discovery
---
### Retrieval Depth Governs Reasoning Breadth
Increasing `top_k`:
- increases filtered sentence count
- expands conceptual coverage
- lengthens generation
- increases latency
Retrieval depth acts as a direct control on reasoning complexity.
---
### Generation Latency Is Context-Driven
Latency is dominated by **generation time**, not embedding or chunking.
Primary drivers:
- number of filtered gap sentences
- semantic density of context
- retrieval recall (hybrid > dense)
---
## Configuration Intelligence (v2)
### Best Configuration Detector
Automatically selects the best-performing configuration based on a chosen objective (e.g., gap richness).
### Research Gap Richness Scoring
Scores configurations using:
- gap density
- filtered sentence count
- retrieval breadth
- output informativeness
- latency penalty
### Radar-Based Performance Visualization
Multi-dimensional radar charts compare top configurations across:
- gap density
- filtered signals
- retrieval volume
- output strength
- inverse latency
Higher surface area indicates stronger multi-dimensional research gap performance.
---
## Key Insight
RAG pipelines are **highly sensitive to semantic segmentation structure**.
Chunking is not a preprocessing step —
it is a **primary behavioral control mechanism** for downstream reasoning.
This has direct implications for:
- automated literature reviews
- evidence gap mapping
- research synthesis systems
- scientific discovery tooling
---
## Current Limitations
- Heuristic (keyword-based) gap detection
- Fixed chunk sizing (non-adaptive)
- No semantic deduplication of gaps
- No statistical significance testing
- Single-document focus
---
## Scope Summary
**v1 established:**
- modular RAG pipeline
- configuration comparison framework
- experiment logging
- empirical sensitivity analysis
**v2 introduced:**
- objective-driven configuration selection
- automated experiment sweeps
- configuration intelligence layer
- radar-based performance visualization
---
## Purpose
This system is built to **extract meaningful, evidence-backed research gaps from real academic literature**, not to generate generic future work statements.
It functions both as:
- a practical research analysis tool
- an experimental environment for studying structured RAG behavior
---
## Roadmap
Planned research directions:
- adaptive chunk sizing
- semantic gap deduplication
- diversity-aware gap scoring
- configuration stability analysis
- research-paper-ready reporting
