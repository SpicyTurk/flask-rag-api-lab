CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "customer_success_knowledge"
DEFAULT_TOP_K = 3


def get_chroma_collection(path=CHROMA_PATH, collection_name=COLLECTION_NAME):
    """Return a persistent Chroma collection for manual local testing."""
    import chromadb 

    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(collection_name)


def _first_list(results, key):
    """Chroma nests each field one level deep (one list per query).

    Return the inner list for the first query, or [] if it is missing.
    """
    value = (results or {}).get(key)
    if not value:
        return []
    return value[0] or []


def format_chroma_results(results):
    """Normalize Chroma query results into context chunk dictionaries.

    Chroma query results often look like:
        {
            "ids": [["chunk-1"]],
            "documents": [["Text"]],
            "metadatas": [[{"source_id": "SRC-1"}]],
            "distances": [[0.12]]
        }
    """
    ids = _first_list(results, "ids")
    documents = _first_list(results, "documents")
    metadatas = _first_list(results, "metadatas")
    distances = _first_list(results, "distances")

    chunks = []
    for index, document in enumerate(documents):
        if not isinstance(document, str) or not document.strip():
            continue

        metadata = (metadatas[index] if index < len(metadatas) else None) or {}

        chunks.append(
            {
                "id": ids[index] if index < len(ids) else None,
                "text": document.strip(),
                "source_id": metadata.get("source_id"),
                "title": metadata.get("title"),
                "category": metadata.get("category"),
                "section": metadata.get("section"),
                "distance": distances[index] if index < len(distances) else None,
            }
        )

    return chunks


def retrieve_context(question, collection=None, top_k=DEFAULT_TOP_K):
    """Retrieve context chunks for a user question.

    Tests may pass a fake collection. Manual use should call Chroma.
    """
    if not isinstance(question, str) or not question.strip():
        return []

    if collection is None:
        collection = get_chroma_collection()

    results = collection.query(
        query_texts=[question.strip()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return format_chroma_results(results)