"""
RAG service: embed user question, retrieve from Qdrant, generate answer via LLMClient.

Uses Gemini for embeddings and LLMClient (Gemini→Groq→OpenAI) for generation.
Optionally saves chat history for authenticated users.
"""
import os
from google import genai
from google.genai import types
from qdrant_client import QdrantClient

from services.llm_client import get_llm_client, AllProvidersExhaustedError
from services.chat_history_service import save_message as save_chat_message

# Google GenAI client (for embeddings only — generation uses LLMClient)
_genai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

# Qdrant client
_qdrant = QdrantClient(
    url=os.environ.get("QDRANT_URL", ""),
    api_key=os.environ.get("QDRANT_API_KEY", ""),
    timeout=60,
)

COLLECTION_NAME = "book_content"
EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are a helpful study companion for the Physical AI & Humanoid Robotics textbook.\
 Answer questions based ONLY on the provided textbook context. If the context doesn't contain \
enough information to answer, say so honestly. Keep answers concise, accurate, and educational.\
 When referencing specific chapters or sections, mention them by name.\
 Stay on topic — only answer questions related to Physical AI, ROS 2, robotics, and the textbook content.\
 If a question is clearly off-topic, politely redirect: \
"I'm designed to help with the Physical AI textbook content. Could you ask something about the topics covered?"
"""


def embed(text: str) -> list[float]:
    """Embed text using Gemini gemini-embedding-001 via native Google GenAI SDK."""
    result = _genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def retrieve(query_embedding: list[float], limit: int = 5) -> list[dict]:
    """Search Qdrant for relevant textbook chunks."""
    results = _qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        score_threshold=0.4,
    )
    return [
        {
            "text": hit.payload.get("text", ""),
            "chapter": hit.payload.get("chapter", ""),
            "heading": hit.payload.get("heading", ""),
            "page_title": hit.payload.get("page_title", ""),
            "score": hit.score,
        }
        for hit in results.points
    ]


async def generate_answer(question: str, selected_text: str | None = None, user_id: int | None = None) -> dict:
    """Full RAG pipeline: embed → retrieve → generate via LLMClient failover.

    Args:
        question: The user's question.
        selected_text: Optional highlighted text for scoped answers.
        user_id: Optional authenticated user ID (enables chat history saving).

    Returns:
        Dict with 'answer' and 'sources' keys.
    """
    # 1. Embed the question (still uses Gemini directly — sync)
    query_embedding = embed(question)

    # 2. Retrieve relevant chunks
    chunks = retrieve(query_embedding)

    # 3. Build context from retrieved chunks
    context_parts = []
    sources = []
    for chunk in chunks:
        context_parts.append(
            f"[From: {chunk['page_title']} — {chunk['heading']}]\n{chunk['text']}"
        )
        source = f"{chunk['page_title']} — {chunk['heading']}"
        if source not in sources:
            sources.append(source)

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

    # 4. Build user message
    user_message = f"Question: {question}"
    if selected_text:
        user_message = (
            f"The user highlighted the following passage from the textbook:\n"
            f'"{selected_text}"\n\n'
            f"Question about this passage: {question}"
        )

    # 5. Call LLM via failover client
    llm = get_llm_client()
    prompt = f"Textbook context:\n{context}\n\n{user_message}"
    answer = await llm.generate(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        max_tokens=1024,
        temperature=0.3,
    )

    if not answer:
        answer = "I couldn't generate an answer. Please try again."

    # 6. Save to chat history if user is authenticated
    if user_id is not None:
        try:
            await save_chat_message(
                user_id=user_id,
                question=question,
                answer=answer,
                selected_text=selected_text,
                sources=sources,
            )
        except Exception:
            # Don't fail the response if history saving fails
            pass

    return {"answer": answer, "sources": sources}
