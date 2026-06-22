import os
import asyncio
from dotenv import load_dotenv
from pypdf import PdfReader
from lightrag import LightRAG, QueryParam
from lightrag.llm.gemini import gemini_complete_if_cache, gemini_embed
from lightrag.utils import wrap_embedding_func_with_attrs
import logging
import os

logging.basicConfig(level=logging.ERROR)
for logger_name in [
    "lightrag",
    "nano-vectordb",
    "google_genai",
    "google",
    "asyncio"
]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)
    logging.getLogger(logger_name).propagate = False

# Optional: completely silence root warnings
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

WORKING_DIR = "./lightrag_storage"
PDF_FILE = "rich-dad-poor-dad.pdf"

LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001")
EMBEDDING_DIM = int(
    os.getenv("EMBEDDING_DIM", "1536"))
EMBEDDING_TOKEN_LIMIT = int(
    os.getenv("EMBEDDING_TOKEN_LIMIT", "2048"))


async def llm_model_func(prompt,system_prompt=None,history_messages=None,**kwargs,):
    return await gemini_complete_if_cache(
        model=LLM_MODEL,
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages or [],
        api_key=os.getenv("GEMINI_API_KEY"),
        **kwargs,
    )


@wrap_embedding_func_with_attrs(
    embedding_dim=EMBEDDING_DIM,
    max_token_size=EMBEDDING_TOKEN_LIMIT,
    model_name=EMBEDDING_MODEL,
)
async def embedding_func(texts):
    result = await gemini_embed.func(
        texts,
        api_key=os.getenv("GEMINI_API_KEY"),
        model=EMBEDDING_MODEL,
    )


    return result

def extract_pages(pdf_path, start_page=14, num_pages=15):
    reader = PdfReader(pdf_path)
    pages = []
    end_page = min(start_page + num_pages, len(reader.pages))

    for i in range(start_page, end_page):
        text = reader.pages[i].extract_text()
        if text:
            pages.append(text)

    return "\n\n".join(pages)


async def main():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        llm_model_name=LLM_MODEL,
        embedding_func=embedding_func,
    )

    await rag.initialize_storages()

    graph_file = os.path.join(
        WORKING_DIR,
        "graph_chunk_entity_relation.graphml"
    )

    if not os.path.exists(graph_file):
        print("Reading PDF...")
        text = extract_pages(PDF_FILE, start_page=14, num_pages=15)
        # print(f"Loaded {len(text):,} characters")
        # print("Ingesting into LightRAG...")
        await rag.ainsert(text)
        # print("Ingestion complete!")

    else:
        print("Existing knowledge graph found.")
    print("\nLightRAG Ready")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Question: ").strip()

        if query.lower() in ["exit", "quit"]:
            break
        try:
            answer = await rag.aquery(
                query,
                param=QueryParam(mode="hybrid")
            )

            print("\nAnswer:")
            print(answer)
            print()
        except Exception as e:
            print(f"\nError: {e}\n")
    await rag.finalize_storages()

if __name__ == "__main__":
    asyncio.run(main())