from .local_embedding import embed_local
from .openai_embedding import embed_openai
from utils.timers import Timer

def embed_chunks(chunks, model_type):
    timer = Timer()
    timer.start()

    if model_type == "local":
        vectors = embed_local(chunks)
    elif model_type == "openai":
        vectors = embed_openai(chunks)
    else:
        raise ValueError("Invalid embedding model")

    elapsed = timer.stop()
    return vectors, elapsed
