def format_context_chunk(chunk):
    """Format one retrieved chunk for the prompt context block."""
    return (
        f"[Source ID: {chunk.get('source_id')}]\n"
        f"Title: {chunk.get('title')}\n"
        f"Category: {chunk.get('category')}\n"
        f"Section: {chunk.get('section')}\n"
        f"Text: {chunk.get('text')}"
    )


def build_rag_prompt(question, context_chunks):
    """Build a structured RAG prompt from a question and retrieved context."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    usable_chunks = [
        chunk
        for chunk in (context_chunks or [])
        if isinstance(chunk.get("text"), str) and chunk["text"].strip()
    ]
    if not usable_chunks:
        raise ValueError("context_chunks must contain at least one usable chunk.")

    context_block = "\n\n".join(format_context_chunk(c) for c in usable_chunks)

    return (
        "Instructions:\n"
        "Use only the approved context"
        "below to answer the question. Do not invent details, policies, or "
        "numbers that are not stated in the context. If the context does not "
        "contain enough information, say what information is missing.\n\n"
        "Context:\n"
        f"{context_block}\n\n"
        "Question:\n"
        f"{question.strip()}\n\n"
        "Response Requirements:\n"
        "- Use only the approved context.\n"
        "- Do not invent unsupported details.\n"
        "- Identify missing information when the context is not enough.\n"
        "- Answer concisely.\n"
        "- Refer to source IDs when helpful.\n"
    )