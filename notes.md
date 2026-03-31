# v3.0 Goal
Transform the pipeline from configuration exploration into a self-optimizing, evidence-backed research system.
## 1. Auto-Adaptive Chunking (Core Upgrade)
Status: Not started
Why: Chunk size is currently the strongest control variable.
What to add
Dynamic chunk sizing based on:
document length
sentence density
section boundaries (abstract vs methods vs discussion)
Replace fixed chunk size with:
target_chunk_count or semantic windowing
Outcome
Reduced fragmentation
Higher gap density consistency
Less manual tuning
Deliverable
Adaptive chunker module
Logged comparison vs fixed chunking
## 2. Semantic Gap Deduplication & Clustering
Status: Not started
Why: High gap counts ≠ meaningful diversity.
What to add
Embed extracted gap sentences
Cluster semantically similar gaps
Deduplicate near-identical statements
Metrics to log
raw gap count
unique gap clusters
redundancy ratio
Outcome
Cleaner, paper-ready gap sets
Higher conceptual richness, not just volume
## 3. Config Confidence Scoring (Statistical Layer)
Status: Not started
Why: “Best config” needs confidence, not just ranking.
What to add
Run repeated trials per configuration
Compute:
mean gap richness
variance
stability score
Optional
Bootstrap confidence intervals
Rank configs by expected performance + stability
Outcome
Best config ≠ lucky run
Research-grade reproducibility
## 4. Multi-Objective Optimization Engine
Status: Partially started (richness vs balanced)
Extend to
Richness
Diversity (penalty-aware)
Latency
Stability
What to add
Pareto frontier selection
User-selectable research objective
Config recommendations per objective
Outcome
Not “one best config”
But best config for your research goal
## 5. Paper-Grade Experiment Report Generator
Status: Not started
Why: Your system already has results — they’re just not structured.
What to add
Auto-generate:
experiment tables
config sensitivity summaries
key findings text (not LLM fluff)
Export as:
Markdown
LaTeX-ready sections
Outcome
Zero friction from experiment → paper draft
Massive leverage for academic writing
