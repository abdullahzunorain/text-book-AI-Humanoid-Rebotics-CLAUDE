"""
RAG service: embed user question, retrieve from Qdrant, generate answer via Gemini.
"""
import os
from google import genai
from google.genai import types
from qdrant_client import QdrantClient

# Google GenAI client (native API for both embeddings and chat)
_genai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

# Qdrant client
_qdrant = QdrantClient(
    url=os.environ.get("QDRANT_URL", ""),
    api_key=os.environ.get("QDRANT_API_KEY", ""),
    timeout=60,
)

COLLECTION_NAME = "book_content"
EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-2.0-flash"

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


def generate_answer(question: str, selected_text: str | None = None) -> dict:
    """Full RAG pipeline: embed → retrieve → generate."""
    # 1. Embed the question
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

    # 5. Call Gemini via native GenAI SDK
    response = _genai_client.models.generate_content(
        model=CHAT_MODEL,
        contents=f"Textbook context:\n{context}\n\n{user_message}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=1024,
            temperature=0.3,
        ),
    )

    answer = response.text or "I couldn't generate an answer. Please try again."

    return {"answer": answer, "sources": sources}
