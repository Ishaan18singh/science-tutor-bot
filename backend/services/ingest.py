import os
import sys
import fitz  # PyMuPDF
import faiss
import pickle
import numpy as np
try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:
    raise ImportError(
        "sentence_transformers is required. Install it with 'pip install sentence-transformers'"
    ) from exc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONTENT_PATH, VECTOR_STORE_PATH, EMBEDDING_MODEL

print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

chunk_size = 500
chunk_overlap = 100

def split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap):
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be larger than chunk_overlap")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        if end == text_length:
            break
        start = end - chunk_overlap

    return chunks


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


def ingest_all():
    all_chunks = []
    all_metadata = []

    for subject in os.listdir(CONTENT_PATH):
        subject_path = os.path.join(CONTENT_PATH, subject)
        if not os.path.isdir(subject_path):
            continue

        for cls in os.listdir(subject_path):
            cls_path = os.path.join(subject_path, cls)
            if not os.path.isdir(cls_path):
                continue

            for chapter in os.listdir(cls_path):
                chapter_path = os.path.join(cls_path, chapter)
                if not os.path.isdir(chapter_path):
                    continue

                for file in os.listdir(chapter_path):
                    text = ""

                    if file.endswith(".pdf"):
                        file_path = os.path.join(chapter_path, file)
                        print(f"📄 Ingesting PDF: {subject}/{cls}/{chapter}/{file}")
                        text = extract_text_from_pdf(file_path)

                    elif file.endswith(".txt"):
                        file_path = os.path.join(chapter_path, file)
                        print(f"📄 Ingesting TXT: {subject}/{cls}/{chapter}/{file}")
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()

                    else:
                        continue  # skip .gitkeep and other files

                    if not text.strip():
                        print(f"   ⚠️  Empty file skipped: {file}")
                        continue

                    chunks = split_text(text)
                    print(f"   ✅ {len(chunks)} chunks created")

                    for chunk in chunks:
                        all_chunks.append(chunk)
                        all_metadata.append({
                            "subject": subject,
                            "class": cls,
                            "chapter": chapter,
                            "source": file,
                            "text": chunk
                        })

    return all_chunks, all_metadata


def save_to_faiss(chunks, metadata):
    print(f"\n🔢 Embedding {len(chunks)} chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "index.faiss"))

    with open(os.path.join(VECTOR_STORE_PATH, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)

    print(f"✅ FAISS index saved with {index.ntotal} vectors")
    print(f"✅ Metadata saved with {len(metadata)} entries")


if __name__ == "__main__":
    chunks, metadata = ingest_all()

    if not chunks:
        print("\n❌ No content found. Check your content/ folders.")
    else:
        save_to_faiss(chunks, metadata)
        print("\n🎉 Ingestion complete! Ready for retrieval.")