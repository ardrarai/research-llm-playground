import time
from .local_embedding import embed_local


def embed_chunks(chunks, model_type="local"):
    """
    Embed text chunks using LOCAL embedding backend only.

    Parameters
    ----------
    chunks : list[str]
        Text chunks to embed.

    model_type : str
        Ignored. Kept only for pipeline compatibility.

    Returns
    -------
    vectors : list
    embedding_time : float
    """

    start = time.time()

    vectors = embed_local(chunks)

    elapsed = time.time() - start

    return vectors, elapsed
