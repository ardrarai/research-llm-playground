from dataclasses import dataclass
from typing import Optional

@dataclass
class PipelineConfig:
    chunk_size: Optional[int]
    chunk_overlap: int
    embedding_model: str
    retrieval_mode: str
    top_k: int
    temperature: float
    prompt_mode: str
    chunking_mode: str = "fixed"  # "fixed" | "adaptive"
