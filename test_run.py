from pipeline.orchestrator import run_pipeline
from utils.config_schema import PipelineConfig

config = PipelineConfig(
    chunk_size=500,
    chunk_overlap=50,
    embedding_model="local",
    retrieval_mode="dense",
    top_k=5,
    temperature=0.2,
    prompt_mode="structured"
)

result = run_pipeline(config, "sample.pdf", "What research gaps exist?")
print(result["output"])
print(result["metrics"])
