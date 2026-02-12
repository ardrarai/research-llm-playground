def build_prompt(query, context_chunks, mode):

    context = "\n\n".join(context_chunks)

    if mode == "conservative":
        instruction = "Answer strictly based on provided context."
    elif mode == "creative":
        instruction = "Provide analytical and exploratory research gaps."
    elif mode == "structured":
        instruction = "Provide research gaps in structured bullet format."
    else:
        instruction = ""

    return f"""
    {instruction}

    Context:
    {context}

    Question:
    {query}
    """
