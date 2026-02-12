from dataclasses import dataclass

@dataclass
class PipelineConfig:
    chunk_size: int
    chunk_overlap: int
    embedding_model: str   # "local" 
    retrieval_mode: str    # "dense", "bm25", "hybrid"
    top_k: int
    temperature: float
    prompt_mode: str       # "conservative", "creative", "structured"
