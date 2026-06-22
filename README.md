# LightRAG Gemini PDF Assistant

A command-line question-answering tool that builds a knowledge graph from a PDF document and lets you query it conversationally using Google Gemini and [LightRAG](https://github.com/HKUDS/LightRAG).

The script extracts text from a PDF, ingests it into a LightRAG knowledge graph (entities, relationships and vector embeddings) and then answers natural-language questions about the document using hybrid retrieval (graph + vector search).

## Features

- 📄 Extracts and ingests text from a specified page range of a PDF
- 🧠 Builds a persistent knowledge graph using LightRAG
- 🔍 Hybrid retrieval (graph traversal + semantic vector search) for accurate answers
- 🤖 Powered by Google Gemini for both language generation and embeddings
- 💾 Caches the knowledge graph locally so re-running the script skips re-ingestion
- 💬 Simple interactive CLI for asking questions

## How It Works

1. On first run, the script reads a configurable page range from your PDF and extracts the text.
2. The text is ingested into LightRAG, which builds an entity-relationship knowledge graph and stores vector embeddings.
3. The graph and embeddings are saved to a local working directory, so future runs reuse the existing graph instead of rebuilding it.
4. You can then ask questions interactively, and LightRAG retrieves relevant context (via hybrid graph + vector search) before generating an answer with Gemini.

## Requirements

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Muhammad-Shiraz/lightrag-pdf-assistant.git
   cd lightrag-pdf-assistant
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install lightrag-hku pypdf python-dotenv google-genai
   ```

4. Create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   LLM_MODEL=gemini-2.5-flash
   EMBEDDING_MODEL=gemini-embedding-001
   EMBEDDING_DIM=1536
   EMBEDDING_TOKEN_LIMIT=2048
   ```

5. Place the PDF you want to query in the project root and update the `PDF_FILE` variable in the script if the filename differs.

## Usage

Run the script:

```bash
python main.py
```

On first run, it will:
- Extract text from the configured page range of your PDF
- Build and save a knowledge graph to `./lightrag_storage`

On subsequent runs, it will detect the existing knowledge graph and skip re-ingestion.

You'll then see a prompt:

```
LightRAG Ready
Type 'exit' to quit.

Question:
```

Type any question about the PDF content and press Enter. Type `exit` or `quit` to end the session.

## Configuration

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key | *(required)* |
| `LLM_MODEL` | Gemini model used for answering questions | `gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Gemini model used for embeddings | `gemini-embedding-001` |
| `EMBEDDING_DIM` | Embedding vector dimension | `1536` |
| `EMBEDDING_TOKEN_LIMIT` | Max tokens per embedding chunk | `2048` |

You can also adjust which pages of the PDF are ingested by editing the `extract_pages()` call in `main()`:

```python
text = extract_pages(PDF_FILE, start_page=14, num_pages=15)
```

## Project Structure

```
.
├── main.py                # Main script
├── .env                   # API keys and config (not committed)
├── lightrag_storage/      # Auto-generated knowledge graph & vector store
└── README.md
```

## Notes

- Delete the `lightrag_storage/` directory if you want to force a fresh re-ingestion of the PDF (e.g., after changing the page range).
- Logging is suppressed by default for a cleaner CLI experience; adjust the logging configuration in the script if you need debug output.
