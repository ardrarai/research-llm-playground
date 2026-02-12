import ollama
from utils.timers import Timer


def generate_answer(query, context_chunks, temperature, prompt_mode):

    timer = Timer()
    timer.start()

    max_sentences = 8
    context = "\n\n".join(context_chunks[:max_sentences])

    system_prompt = """
    You are a research analyst.

    Based strictly on the extracted academic sentences,
    identify 3–5 concise research gaps.

    Be direct.
    Avoid repetition.
    """

    user_prompt = f"""
    Context:
    {context}

    Research Question:
    {query}
    """

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        options={
            "temperature": temperature,
            "num_predict": 300   # limits output length
        }
    )

    output = response["message"]["content"]

    elapsed = timer.stop()

    return output, elapsed
