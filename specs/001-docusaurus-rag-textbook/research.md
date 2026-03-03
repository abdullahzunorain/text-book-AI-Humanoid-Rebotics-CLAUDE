# Phase 0 Research: Docusaurus RAG Textbook

**Branch**: `001-docusaurus-rag-textbook` | **Date**: 2026-03-03 | **Plan**: [plan.md](plan.md)

---

## 1. Docusaurus 3 DocItem Swizzling

### Decision

Swizzle `@theme/DocItem/Layout` using the **wrapping** strategy. Create `website/src/theme/DocItem/Layout/index.tsx` that imports the original component and wraps it with `<ChatbotWidget />` and `<SelectedTextHandler />`.

```tsx
// website/src/theme/DocItem/Layout/index.tsx
import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type { WrapperProps } from '@docusaurus/types';
import ChatbotWidget from '@site/src/components/ChatbotWidget';
import SelectedTextHandler from '@site/src/components/SelectedTextHandler';

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): JSX.Element {
  return (
    <>
      <Layout {...props} />
      <ChatbotWidget />
      <SelectedTextHandler />
    </>
  );
}
```

**Swizzle command** (for reference, manual creation preferred for control):
```bash
npx docusaurus swizzle @docusaurus/theme-classic DocItem/Layout --wrap --typescript
```

### Rationale

- **Wrapping** (not ejecting) is the recommended strategy for injecting siblings. It preserves all upstream DocItem behavior and is resilient to Docusaurus minor/patch updates.
- The swizzle path `DocItem/Layout` is the correct granularity — it wraps the entire doc page layout (content + TOC + metadata) and renders once per page navigation. Swizzling `DocItem` (the parent) is possible but `DocItem/Layout` is more stable and targeted.
- Docusaurus 3 uses a component hierarchy: `DocItem` → `DocItem/Layout` → `DocItem/Content`, `DocItem/TOC`, `DocItem/Footer`, etc. Wrapping at `Layout` level means our components render alongside the doc content on every docs page.
- The `@theme-original` import alias is how Docusaurus resolves the original component when wrapping—this is a Docusaurus convention, not a general webpack/React pattern.

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **Eject DocItem/Layout** | Copies entire source; breaks on Docusaurus updates; unnecessary since we only add siblings |
| **Swizzle DocItem (root)** | Less stable swizzle target (marked "unsafe" in some versions); Layout is safer |
| **Docusaurus plugin (client module)** | Could inject via `clientModules` in plugin, but cannot easily target only doc pages; swizzling is cleaner for doc-page-only components |
| **Custom Docusaurus plugin with `contentLoaded`** | Over-engineered for injecting React components; contentLoaded is for route/data generation, not UI injection |
| **MDX component injection via MDXComponents** | Requires adding `<ChatbotWidget />` to every .md file or using remark plugin; fragile and repetitive |

---

## 2. Gemini via OpenAI Python SDK

### Decision

Use the `openai` Python package (v1.x) pointed at Google's Gemini OpenAI-compatible endpoint. Two clients:

**Chat completions (Gemini 2.0 Flash):**
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {"role": "system", "content": "You are a helpful textbook assistant..."},
        {"role": "user", "content": user_query}
    ],
    max_tokens=1024,
    temperature=0.3
)
answer = response.choices[0].message.content
```

**Embeddings (text-embedding-004):**
```python
embedding_client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

result = embedding_client.embeddings.create(
    model="text-embedding-004",
    input="Some text to embed"
)
vector = result.data[0].embedding  # 768 dimensions
```

### Rationale

- Google provides an official OpenAI-compatible REST API at `https://generativelanguage.googleapis.com/v1beta/openai/`. This means the standard `openai` Python SDK works out of the box—no Google-specific SDK needed.
- Single dependency (`openai`) for both chat and embeddings, reducing backend complexity.
- `gemini-2.0-flash` is the fast, cost-effective model — ideal for a chatbot that needs <5s p95 latency.
- `text-embedding-004` produces 768-dimensional vectors by default, which is efficient for Qdrant storage on the free tier.
- The API key is a standard Google AI Studio API key (not a GCP service account).

### Gotchas

1. **base_url trailing slash**: The URL **must** end with `/openai/` (trailing slash). Without it, requests fail with 404.
2. **Model string format**: Use `gemini-2.0-flash` (not `models/gemini-2.0-flash`). The `/openai/` endpoint handles the prefix internally. For embeddings, use `text-embedding-004` (not `models/text-embedding-004`).
3. **Streaming**: `stream=True` is supported but adds complexity. For MVP, use non-streaming (simpler error handling).
4. **Function calling / tools**: Supported but not needed for this project.
5. **Rate limits**: Free tier has generous limits (15 RPM for Flash, 1500 RPD). Sufficient for MVP but would need monitoring at scale.
6. **`max_tokens` vs `max_completion_tokens`**: Use `max_tokens` — the Gemini compatibility layer maps it correctly.

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **google-generativeai SDK** | Google-specific; adds a second SDK pattern; openai SDK is more portable |
| **google-cloud-aiplatform (Vertex AI)** | Requires GCP project, service account, OAuth — violates simplicity constraint |
| **LangChain ChatGoogleGenerativeAI** | Heavy dependency for one LLM call; over-engineered for single-endpoint use |
| **Direct REST calls (requests/httpx)** | Reinvents auth, retry, parsing that openai SDK already handles |

---

## 3. Qdrant Cloud Free Tier

### Decision

Use Qdrant Cloud free tier with a single collection `book_content`:
- **768 dimensions** (matching text-embedding-004 output)
- **Cosine** distance metric
- **~30–50 vectors** (one per content chunk)

**Collection creation and usage:**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(
    url=os.environ["QDRANT_URL"],       # e.g., https://xxx.us-east4-0.gcp.cloud.qdrant.io:6333
    api_key=os.environ["QDRANT_API_KEY"]
)

# Create collection (idempotent — call once during indexing)
client.recreate_collection(
    collection_name="book_content",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

# Upsert chunks
client.upsert(
    collection_name="book_content",
    points=[
        PointStruct(
            id=i,
            vector=embedding_vector,      # 768-dim list
            payload={
                "text": chunk_text,
                "chapter": "01-architecture",
                "module": "module1-ros2",
                "page_title": "ROS 2 Architecture",
                "heading": "## Nodes and Executors"
            }
        )
        for i, (embedding_vector, chunk_text) in enumerate(chunks)
    ]
)

# Search
results = client.search(
    collection_name="book_content",
    query_vector=query_embedding,   # 768-dim
    limit=3,
    score_threshold=0.5             # Filter low-relevance results
)
```

### Free Tier Limits

| Resource | Limit |
|---|---|
| Clusters | 1 |
| Vectors | ~1M (1 GB storage) |
| RAM | 0.5 GB |
| Disk | 1 GB (total, shared across collections) |
| Collections | Unlimited (within storage) |
| API rate | Not explicitly limited; fair-use |
| Cloud regions | Limited selection (US, EU) |
| Backups | None on free tier |

Our usage (~50 vectors × 768 dims × 4 bytes = ~150 KB) is well within all limits.

### Rationale

- Qdrant Cloud free tier is generous enough for this project by orders of magnitude.
- `qdrant-client` is a well-maintained Python SDK with sync and async support.
- Cosine distance is standard for text embeddings and matches text-embedding-004's normalized outputs.
- Integer IDs (0, 1, 2, ...) are simplest for a small, static collection. UUIDs would add complexity without benefit.
- `score_threshold=0.5` provides a reasonable cutoff to avoid returning irrelevant chunks.

### Best Practices for Small Collections

1. **No need for HNSW tuning** — At <100 vectors, exact search is fast. Qdrant defaults work fine.
2. **Use `recreate_collection`** during indexing to ensure a clean state.
3. **Store rich payloads** — Include chapter, module, page_title, heading in each point. This enables filtered search and provides context for the LLM prompt.
4. **Use `search` not `query`** — `search` is the standard vector similarity method (`query` is for more complex scenarios).

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **Pinecone free tier** | Similar capability but Qdrant's Python client is more Pythonic; Pinecone's free tier requires a starter index with limited metadata filtering |
| **ChromaDB (self-hosted)** | Requires persistent storage on the server; adds operational complexity on Railway |
| **FAISS (in-memory)** | No persistence; vectors lost on server restart; would need to re-index on every deploy |
| **Weaviate Cloud** | Free tier is more limited; Qdrant is simpler for pure vector search without a schema |
| **pgvector (Supabase)** | Over-engineered; adds a Postgres dependency for 50 vectors |

---

## 4. FastAPI CORS for GitHub Pages

### Decision

Use FastAPI's `CORSMiddleware` with explicit origin allowlist:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://<username>.github.io",           # GitHub Pages domain
    "http://localhost:3000",                    # Local Docusaurus dev
    "http://localhost:3001",                    # Alternate local port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,        # No cookies/auth
    allow_methods=["POST", "OPTIONS"],  # Only POST /api/chat + preflight
    allow_headers=["Content-Type"],
)
```

### Rationale

- **Explicit origins** over `allow_origins=["*"]` is best practice, even for a public API. It prevents unauthorized sites from making credentialed requests (though we use no credentials).
- GitHub Pages serves from `https://<username>.github.io` (or `https://<org>.github.io/<repo>` — both share the same origin `https://<username>.github.io`).
- Only `POST` and `OPTIONS` are needed (POST for chat, OPTIONS for CORS preflight). No GET, PUT, DELETE.
- `allow_headers=["Content-Type"]` is sufficient since we send JSON. No Authorization header needed.
- `allow_credentials=False` is correct — we have no auth, no cookies.
- The middleware handles preflight (`OPTIONS`) requests automatically.

### Key Details

- **GitHub Pages origin**: If the repo is `user/repo`, the site is at `https://user.github.io/repo/` but the **origin** for CORS is `https://user.github.io` (port is implicit 443, path is not part of origin).
- **Railway domain**: The API will be at something like `https://your-app.up.railway.app`. The frontend makes cross-origin requests to this URL.
- **Preflight caching**: Add `max_age=3600` to `CORSMiddleware` to cache preflight responses for 1 hour, reducing OPTIONS requests.

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **`allow_origins=["*"]`** | Works but is less secure; not recommended when origins are known |
| **Reverse proxy (nginx)** | Adds infrastructure complexity; Railway handles HTTPS termination already |
| **Same-origin deployment (API on Pages)** | Impossible — Pages is static-only; cannot serve FastAPI |
| **Vercel serverless functions** | Could co-locate frontend+API but Docusaurus on Vercel adds cold-start latency; keeping them separate is cleaner |

---

## 5. Markdown Chunking by Headings

### Decision

Use a simple regex-based Python approach to split markdown files by H2/H3 headings, then enforce a max token limit of ~400 tokens per chunk. No external library needed.

```python
import re

def chunk_markdown(filepath: str, max_tokens: int = 400) -> list[dict]:
    """Split a markdown file into chunks by H2/H3 headings."""
    with open(filepath, "r") as f:
        content = f.read()

    # Extract frontmatter metadata if present
    meta = {}
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip()
        content = content[fm_match.end():]

    # Split by H2 or H3 headings (keep heading with its section)
    sections = re.split(r'(?=^#{2,3}\s)', content, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract heading
        heading_match = re.match(r'^(#{2,3})\s+(.*)', section)
        heading = heading_match.group(2) if heading_match else "Introduction"

        # Simple token estimation: split by whitespace
        tokens = section.split()
        if len(tokens) <= max_tokens:
            chunks.append({
                "text": section,
                "heading": heading,
                "page_title": meta.get("title", filepath),
                "chapter": filepath.split("/")[-1].replace(".md", ""),
                "module": _infer_module(filepath),
                "token_count": len(tokens)
            })
        else:
            # Split oversized sections by paragraph
            paragraphs = section.split("\n\n")
            current_chunk = []
            current_count = 0
            for para in paragraphs:
                para_tokens = len(para.split())
                if current_count + para_tokens > max_tokens and current_chunk:
                    chunks.append({
                        "text": "\n\n".join(current_chunk),
                        "heading": heading,
                        "page_title": meta.get("title", filepath),
                        "chapter": filepath.split("/")[-1].replace(".md", ""),
                        "module": _infer_module(filepath),
                        "token_count": current_count
                    })
                    current_chunk = [para]
                    current_count = para_tokens
                else:
                    current_chunk.append(para)
                    current_count += para_tokens
            if current_chunk:
                chunks.append({
                    "text": "\n\n".join(current_chunk),
                    "heading": heading,
                    "page_title": meta.get("title", filepath),
                    "chapter": filepath.split("/")[-1].replace(".md", ""),
                    "module": _infer_module(filepath),
                    "token_count": current_count
                })

    return chunks

def _infer_module(filepath: str) -> str:
    if "module1" in filepath:
        return "module1-ros2"
    elif "intro" in filepath:
        return "introduction"
    return "unknown"
```

### Rationale

- **Regex splitting by headings** is reliable for well-structured markdown (which we control). The pattern `(?=^#{2,3}\s)` uses a lookahead to split while keeping the heading attached to its section.
- **400-token limit** (~300 words) balances: small enough for focused retrieval, large enough for meaningful context. With Gemini's context window, we can fit 3 retrieved chunks + system prompt + user query comfortably.
- **Whitespace tokenization** for counting is a reasonable approximation (1 word ≈ 1.3 tokens). For 400 "word tokens," actual LLM tokens will be ~520, which is fine.
- **Metadata per chunk** (chapter, module, page_title, heading) enables: (a) filtered searches if needed, (b) citation in chatbot responses ("From Chapter 2: Nodes and Topics"), (c) debugging which chunks are retrieved.
- **No external dependency** — The markdown files are author-controlled and follow a predictable structure. Libraries like `langchain.text_splitters` or `llama_index` add heavy dependencies for minimal gain over this 60-line function.

### Chunking Strategy Details

- **H1 headings** (chapter titles) are not split points — they're metadata, not section dividers.
- **Code blocks** remain within their parent section. Code fences (```) are preserved in chunk text so the LLM can reference them.
- **Frontmatter** (YAML between `---` markers) is extracted for metadata but not included in chunk text.
- **Oversized sections** (>400 tokens) are sub-split by paragraph (`\n\n`). This handles long prose sections while keeping code blocks intact (code blocks rarely contain `\n\n`).
- **Expected output**: ~30–50 chunks across 7 pages (average ~5–7 chunks per page).

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **LangChain RecursiveCharacterTextSplitter** | Heavy dependency; heading-aware splitting needs custom separators; overkill for 7 files |
| **LlamaIndex SentenceSplitter** | Same dependency concern; designed for larger corpora |
| **Fixed character/token windows with overlap** | Loses semantic boundaries (headings); chunks span unrelated sections |
| **One chunk per page** | Chunks too large (~800–1500 tokens per page); reduces retrieval precision |
| **Split by sentence (nltk/spacy)** | Heavy NLP dependencies for no benefit when heading structure is available |
| **markdown-it / mdast parsing** | Proper AST parsing; more correct but adds Node.js dependency or Python markdown parser; regex is sufficient for our controlled content |

---

## 6. GitHub Pages Deployment for Docusaurus 3

### Decision

Use the official Docusaurus GitHub Actions workflow with deployment to GitHub Pages via `actions/deploy-pages`.

**Key `docusaurus.config.ts` settings:**
```typescript
const config: Config = {
  title: 'Physical AI & ROS 2 Textbook',
  url: 'https://<username>.github.io',     // Your GitHub Pages URL
  baseUrl: '/Hack-I-Copilot/',              // /<repo-name>/
  organizationName: '<username>',            // GitHub org or username
  projectName: 'Hack-I-Copilot',            // GitHub repo name
  trailingSlash: false,
  deploymentBranch: 'gh-pages',             // Default; usually not needed if using Actions
  // ...
};
```

**GitHub Actions workflow (`.github/workflows/deploy.yml`):**
```yaml
name: Deploy Docusaurus to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./website
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm
          cache-dependency-path: website/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build
        env:
          REACT_APP_API_URL: ${{ vars.API_URL }}

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: website/build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Rationale

- **`actions/deploy-pages`** is GitHub's recommended approach (over `gh-pages` branch pushes or `peaceiris/actions-gh-pages`). It uses GitHub's Pages deployment API directly.
- **`baseUrl: '/Hack-I-Copilot/'`** is required because GitHub Pages for project repos serves from `https://<user>.github.io/<repo>/`. Without it, all asset paths break.
- **`trailingSlash: false`** avoids 404s on GitHub Pages (which doesn't do server-side redirects for trailing slashes).
- **`working-directory: ./website`** scopes all build commands to the Docusaurus project directory.
- **Environment variable `REACT_APP_API_URL`** is injected at build time so the frontend knows the backend URL. Stored as a GitHub repository variable (not secret — it's a public URL).
- **`concurrency` group** prevents overlapping deployments.

### Key Setup Steps

1. Go to **repo Settings → Pages → Source** and select **"GitHub Actions"** (not "Deploy from branch").
2. Set `vars.API_URL` in **repo Settings → Secrets and variables → Actions → Variables** to the Railway API URL.
3. Ensure the repo is public (GitHub Pages free tier requires public repos, or use GitHub Pro).

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **`docusaurus deploy` command (SSH/token)** | Pushes to `gh-pages` branch; older pattern; `actions/deploy-pages` is more modern and uses environment protection |
| **peaceiris/actions-gh-pages** | Third-party action; `actions/deploy-pages` is first-party and better supported |
| **Vercel deployment** | Free tier works but adds a service; GitHub Pages is simpler for static sites and already integrated |
| **Netlify** | Similar to Vercel concern; GitHub Pages is zero-config for GitHub repos |
| **Cloudflare Pages** | Good option but adds another account/service; GitHub Pages keeps everything in GitHub |

---

## 7. Text Selection Detection in React

### Decision

Use a combination of `mouseup` and `selectionchange` events in a React component. Position a floating popup using the selection's bounding rectangle via `Range.getBoundingClientRect()`.

```tsx
// website/src/components/SelectedTextHandler.tsx
import React, { useState, useEffect, useCallback } from 'react';

interface PopupPosition {
  top: number;
  left: number;
}

export default function SelectedTextHandler() {
  const [selectedText, setSelectedText] = useState('');
  const [showPopup, setShowPopup] = useState(false);
  const [position, setPosition] = useState<PopupPosition>({ top: 0, left: 0 });

  const handleSelection = useCallback(() => {
    const selection = window.getSelection();
    const text = selection?.toString().trim() || '';

    if (text.length > 10) {  // Minimum selection length
      const range = selection!.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      setSelectedText(text);
      setPosition({
        top: rect.top + window.scrollY - 40,  // Above selection
        left: rect.left + window.scrollX + (rect.width / 2),  // Centered
      });
      setShowPopup(true);
    } else {
      setShowPopup(false);
      setSelectedText('');
    }
  }, []);

  useEffect(() => {
    // mouseup catches most desktop selections
    document.addEventListener('mouseup', handleSelection);
    // selectionchange handles keyboard and mobile selections
    document.addEventListener('selectionchange', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('selectionchange', handleSelection);
    };
  }, [handleSelection]);

  // Dismiss on click outside
  useEffect(() => {
    const handleClickOutside = () => {
      const selection = window.getSelection();
      if (!selection?.toString().trim()) {
        setShowPopup(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!showPopup) return null;

  return (
    <div
      className="selection-popup"
      style={{
        position: 'absolute',
        top: position.top,
        left: position.left,
        transform: 'translateX(-50%)',  // Center horizontally
        zIndex: 1000,
      }}
    >
      <button onClick={() => {
        // Dispatch selected text to ChatbotWidget
        window.dispatchEvent(
          new CustomEvent('askAboutSelection', { detail: selectedText })
        );
        setShowPopup(false);
      }}>
        Ask about this
      </button>
    </div>
  );
}
```

### Rationale

- **`mouseup`** is the most reliable event for detecting when a drag-selection completes on desktop.
- **`selectionchange`** fires on the `document` and captures keyboard-based selections (Shift+Arrow) and mobile long-press selections. Using both events provides comprehensive coverage.
- **`Range.getBoundingClientRect()`** returns the visual bounding box of the selected text, enabling precise popup positioning without measuring DOM elements manually.
- **`window.scrollY` offset** converts viewport-relative coordinates to absolute page coordinates, necessary for `position: absolute` on the popup.
- **`CustomEvent` dispatch** for communicating with `ChatbotWidget` is simple one-way messaging without needing React context or a state management library. The ChatbotWidget listens for `askAboutSelection` events.
- **Minimum 10-character threshold** prevents the popup from appearing for accidental clicks or trivial selections.

### Cross-Browser & Mobile Considerations

| Concern | Handling |
|---|---|
| **Safari iOS** | `selectionchange` fires on `document`; Safari supports it. `mouseup` doesn't fire on touch — use `selectionchange` as fallback. |
| **Chrome Android** | Long-press triggers native selection UI → `selectionchange` fires when selection handle is released. Works. |
| **Firefox** | Both `mouseup` and `selectionchange` work. `selectionchange` may fire frequently (on every cursor move) — the debounce from checking `text.length > 10` prevents excessive state updates. |
| **Popup overlap with native context menu** | On mobile, the native selection menu (copy/paste) may overlap. Position popup above selection (`rect.top - 40`) to minimize conflict. |
| **Selection inside code blocks** | `window.getSelection()` captures text from `<code>` and `<pre>` elements. No special handling needed — FR-018 says chatbot should explain selected code. |

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **Popper.js / Floating UI** | Adds a dependency for positioning that can be done with 5 lines of CSS + getBoundingClientRect |
| **React `onMouseUp` on a wrapper div** | Misses selections that start/end outside the wrapper; document-level listener is more reliable |
| **`selectionchange` only** | Fires too frequently on some browsers (every cursor movement); `mouseup` provides a clean "selection complete" signal on desktop |
| **React context for text sharing** | Adds state management complexity; CustomEvent is simpler for cross-component communication between swizzled components |
| **Tooltip library (react-tooltip, tippy.js)** | Dependency overhead for a single floating button; custom positioning is trivial |

---

## 8. Railway Deployment for FastAPI

### Decision

Deploy the FastAPI app to Railway with minimal configuration:

**`backend/Procfile`:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**`backend/requirements.txt`:**
```
fastapi==0.115.*
uvicorn[standard]==0.34.*
openai==1.61.*
qdrant-client==1.13.*
python-dotenv==1.0.*
```

**`backend/runtime.txt`** (optional, Railway auto-detects):
```
python-3.11
```

**Environment variables** (set in Railway dashboard):
- `GEMINI_API_KEY` — Google AI Studio API key
- `QDRANT_URL` — Qdrant Cloud cluster URL
- `QDRANT_API_KEY` — Qdrant Cloud API key

### Railway Setup Steps

1. Connect GitHub repo to Railway.
2. Set **Root Directory** to `backend/` in the service settings (since the repo has `website/` and `backend/` at root).
3. Railway auto-detects Python (sees `requirements.txt`), installs deps, and runs the Procfile.
4. Set environment variables in the Railway dashboard (Settings → Variables).
5. Railway provides a public URL like `https://your-app-production.up.railway.app`.
6. The `$PORT` environment variable is injected by Railway — uvicorn must bind to it.

### Free Tier Limits (Trial Plan)

| Resource | Limit |
|---|---|
| **Execution hours** | 500 hours/month (enough for ~20 days continuous or always-on with sleep) |
| **Memory** | 512 MB (sufficient for FastAPI + uvicorn) |
| **Shared vCPU** | Shared |
| **Network egress** | 100 GB / month |
| **Deploy limit** | No hard limit on deployments |
| **Credit** | $5 free trial credit (one-time, no recurring credit without payment method) |
| **Sleep** | Services sleep after 10 min inactivity; cold start ~2–5s |

**Important**: Railway's free trial gives $5 one-time credit. After that, you need a Hobby plan ($5/month) for continued use. For a hackathon project, the trial credit is sufficient. If the project runs longer, add a payment method for Hobby tier.

### Rationale

- Railway has the simplest Python deployment: push code → auto-deploy. No Dockerfile needed.
- Procfile-based deployment is well-documented and predictable.
- The `$PORT` variable is Railway's standard way to assign ports — uvicorn must use it (not hardcode 8000).
- `uvicorn[standard]` includes `uvloop` and `httptools` for better performance.
- `python-dotenv` enables local development with `.env` files without affecting Railway (which uses dashboard env vars).

### Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| **Vercel (Python serverless)** | Cold starts are slower; debugging serverless Python on Vercel is painful; Railway gives a real server |
| **Render free tier** | Generous free tier but slower deploys; spins down after 15 min inactivity with 30–60s cold starts |
| **Fly.io** | Requires Dockerfile or `fly.toml`; more configuration than Railway |
| **Heroku** | No free tier anymore (eliminated in 2022); Eco plan is $5/month but less polished than Railway |
| **AWS Lambda + API Gateway** | Way over-engineered; requires SAM/Serverless framework; violates simplicity |
| **Google Cloud Run** | Good option but requires GCP setup, Dockerfile, and more configuration |
| **Self-hosted VPS (DigitalOcean, etc.)** | Requires server management, SSL setup, etc.; Railway abstracts all of this |

---

## Summary Matrix

| # | Topic | Decision | Key Risk |
|---|---|---|---|
| 1 | DocItem Swizzling | Wrap `DocItem/Layout` with ChatbotWidget + SelectedTextHandler | Docusaurus major version breaking swizzle paths |
| 2 | Gemini via OpenAI SDK | `openai` Python SDK → `generativelanguage.googleapis.com/v1beta/openai/` | Trailing slash in base_url; rate limits on free tier |
| 3 | Qdrant Cloud | Free tier, 1 collection, 768-dim, cosine, ~50 vectors | Free tier may change; no backups |
| 4 | CORS | Explicit origin allowlist in CORSMiddleware | Must update origins if domain changes |
| 5 | Markdown Chunking | Regex split by H2/H3, max 400 tokens, paragraph sub-split | Edge cases with nested headings or unusual markdown |
| 6 | GitHub Pages Deploy | `actions/deploy-pages` + `baseUrl: '/Hack-I-Copilot/'` | Must set Pages source to "GitHub Actions" in settings |
| 7 | Text Selection | `mouseup` + `selectionchange` + `getBoundingClientRect()` | Mobile native selection menu overlap |
| 8 | Railway Deploy | Procfile + requirements.txt, root dir = `backend/` | $5 trial credit is finite; cold starts after sleep |
