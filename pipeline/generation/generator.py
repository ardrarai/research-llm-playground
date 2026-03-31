# --------------------------------------------
# OPTIONAL OLLAMA IMPORT
# --------------------------------------------
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


# --------------------------------------------
# MAIN GENERATION FUNCTION
# --------------------------------------------

def generate_answer(context, query, mode="conservative"):
    """
    Generates answer using:
    - Ollama (local)
    - Fallback (cloud-safe)
    """

    # -----------------------------
    # LOCAL (OLLAMA)
    # -----------------------------
    if OLLAMA_AVAILABLE:
        try:
            response = ollama.chat(
                model="phi3:mini",
                messages=[
                    {"role": "system", "content": "You are a precise research assistant."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
                ]
            )
            return response["message"]["content"]

        except Exception:
            pass  # fallback if ollama fails

    # -----------------------------
    # FALLBACK (DEPLOYMENT SAFE)
    # -----------------------------
    return fallback_generate(context, query, mode)


# --------------------------------------------
# FALLBACK GENERATION
# --------------------------------------------

def fallback_generate(context, query, mode):
    """
    Lightweight deterministic fallback.
    Ensures system runs without LLM dependency.
    """

    # Simple heuristic output (clean, not garbage)
    context_preview = context[:500] if isinstance(context, str) else str(context)

    return f"""
[Fallback Generation]

Query:
{query}

Observed Context (truncated):
{context_preview}

Note:
LLM generation is disabled in this environment.
This output reflects retrieved signals without generative synthesis.
"""
