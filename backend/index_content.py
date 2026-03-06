"""
Index textbook markdown content into Qdrant.

Usage:
    python index_content.py

Reads all .md files from website/docs/, chunks by H2/H3 headings,
embeds via Gemini text-embedding-004, and upserts to Qdrant.
"""
import os
import re
import glob
import time
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
    timeout=60,
)

COLLECTION_NAME = "book_content"
EMBEDDING_MODEL = "gemini-embedding-001"
VECTOR_SIZE = 3072
MAX_TOKENS = 500
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "website", "docs")


def chunk_markdown(filepath: str, max_tokens: int = MAX_TOKENS) -> list[dict]:
    """Split a markdown file into chunks by H2/H3 headings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter metadata if present
    meta = {}
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip().strip('"').strip("'")
        content = content[fm_match.end() :]

    # Split by H2 or H3 headings (keep heading with its section)
    sections = re.split(r"(?=^#{2,3}\s)", content, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract heading
        heading_match = re.match(r"^(#{2,3})\s+(.*)", section)
        heading = heading_match.group(2) if heading_match else "Introduction"

        # Simple token estimation: split by whitespace
        tokens = section.split()
        if len(tokens) <= max_tokens:
            chunks.append(
                {
                    "text": section,
                    "heading": heading,
                    "page_title": meta.get("title", os.path.basename(filepath)),
                    "chapter": os.path.basename(filepath).replace(".md", ""),
                    "module": _infer_module(filepath),
                    "chapter_slug": _compute_chapter_slug(filepath),
                    "token_count": len(tokens),
                }
            )
        else:
            # Split oversized sections by paragraph
            paragraphs = section.split("\n\n")
            current_chunk: list[str] = []
            current_count = 0
            for para in paragraphs:
                para_tokens = len(para.split())
                if current_count + para_tokens > max_tokens and current_chunk:
                    chunks.append(
                        {
                            "text": "\n\n".join(current_chunk),
                            "heading": heading,
                            "page_title": meta.get(
                                "title", os.path.basename(filepath)
                            ),
                            "chapter": os.path.basename(filepath).replace(".md", ""),
                            "module": _infer_module(filepath),
                            "chapter_slug": _compute_chapter_slug(filepath),
                            "token_count": current_count,
                        }
                    )
                    current_chunk = [para]
                    current_count = para_tokens
                else:
                    current_chunk.append(para)
                    current_count += para_tokens
            if current_chunk:
                chunks.append(
                    {
                        "text": "\n\n".join(current_chunk),
                        "heading": heading,
                        "page_title": meta.get("title", os.path.basename(filepath)),
                        "chapter": os.path.basename(filepath).replace(".md", ""),
                        "module": _infer_module(filepath),
                        "chapter_slug": _compute_chapter_slug(filepath),
                        "token_count": current_count,
                    }
                )

    return chunks


def _infer_module(filepath: str) -> str:
    if "module1" in filepath:
        return "module1-ros2"
    elif "module2" in filepath:
        return "module2-simulation"
    elif "module3" in filepath:
        return "module3-isaac"
    elif "module4" in filepath:
        return "module4-vla"
    elif "intro" in filepath:
        return "introduction"
    return "unknown"


def _compute_chapter_slug(filepath: str) -> str:
    """Compute a chapter slug relative to the docs directory for cache key matching."""
    rel = os.path.relpath(filepath, os.path.abspath(DOCS_DIR))
    slug = rel.replace(".md", "").replace("/index", "")
    return slug


def embed_text(text: str) -> list[float]:
    """Embed a single text string using Google GenAI native SDK."""
    result = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
    return result.embeddings[0].values


def index_all():
    """Main indexing function: chunk all docs, embed, upsert to Qdrant."""
    docs_path = os.path.abspath(DOCS_DIR)
    print(f"Scanning docs at: {docs_path}")

    # Find all markdown files
    md_files = sorted(glob.glob(os.path.join(docs_path, "**", "*.md"), recursive=True))
    print(f"Found {len(md_files)} markdown files")

    # Chunk all files
    all_chunks: list[dict] = []
    for filepath in md_files:
        chunks = chunk_markdown(filepath)
        print(f"  {os.path.relpath(filepath, docs_path)}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")

    if not all_chunks:
        print("No chunks to index. Exiting.")
        return

    # Recreate collection
    print(f"\nRecreating Qdrant collection '{COLLECTION_NAME}'...")
    if qdrant.collection_exists(COLLECTION_NAME):
        qdrant.delete_collection(COLLECTION_NAME)
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Embed and upsert
    points: list[PointStruct] = []
    for i, chunk in enumerate(all_chunks):
        print(f"  Embedding chunk {i + 1}/{len(all_chunks)}: {chunk['heading'][:50]}...")
        vector = embed_text(chunk["text"])
        points.append(
            PointStruct(
                id=i,
                vector=vector,
                payload={
                    "text": chunk["text"],
                    "chapter": chunk["chapter"],
                    "module": chunk["module"],
                    "page_title": chunk["page_title"],
                    "heading": chunk["heading"],
                    "chapter_slug": chunk["chapter_slug"],
                },
            )
        )
        # Rate-limit: small delay between API calls
        time.sleep(0.2)

    print(f"\nUpserting {len(points)} vectors to Qdrant (in batches of 10)...")
    batch_size = 10
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        qdrant.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Upserted batch {start // batch_size + 1}/{(len(points) + batch_size - 1) // batch_size}")
        time.sleep(0.5)
    print("Done! Content indexed successfully.")


if __name__ == "__main__":
    index_all()
