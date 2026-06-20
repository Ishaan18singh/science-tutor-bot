import os
import sys
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VECTOR_STORE_PATH, EMBEDDING_MODEL, CONFIDENCE_THRESHOLD, TOP_K

print("Loading retriever...")
model = SentenceTransformer(EMBEDDING_MODEL)

index = faiss.read_index(os.path.join(VECTOR_STORE_PATH, "index.faiss"))

with open(os.path.join(VECTOR_STORE_PATH, "metadata.pkl"), "rb") as f:
    metadata = pickle.load(f)

print(f"✅ Retriever ready — {index.ntotal} vectors loaded\n")


def retrieve(query: str):
    """
    Returns (chunks, status)
    status: "OK" | "LOW_CONFIDENCE" | "EMPTY_INDEX"
    """

    if index.ntotal == 0:
        return [], "EMPTY_INDEX"

    query_vector = model.encode([query])
    query_vector = np.array(query_vector).astype("float32")

    distances, indices = index.search(query_vector, TOP_K)

    best_distance = distances[0][0]
    confidence_score = 1 / (1 + best_distance)

    print(f"🔍 Query: '{query}'")
    print(f"   Confidence score: {confidence_score:.4f}")

    if confidence_score < CONFIDENCE_THRESHOLD:
        print(f"   ⚠️  LOW CONFIDENCE (threshold: {CONFIDENCE_THRESHOLD})")
        return [], "LOW_CONFIDENCE"

    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        chunk_meta = metadata[idx]
        results.append({
            "text": chunk_meta["text"],
            "subject": chunk_meta["subject"],
            "class": chunk_meta["class"],
            "chapter": chunk_meta["chapter"],
            "source": chunk_meta["source"],
            "score": float(round(1 / (1 + distances[0][i]), 4))
        })

    print(f"   ✅ {len(results)} chunks returned\n")
    return results, "OK"


if __name__ == "__main__":
    test_queries = [
        "What is the law of conservation of mass?",
        "Explain mole concept",
        "What is chemical bonding?",
        "What is photosynthesis?",          # biology - not in chemistry notes
        "Explain Newton's laws of motion",  # physics - not in chemistry notes  
        "Who is the Prime Minister of India?",  # totally unrelated
    ]

    print("="*60)
    print("RETRIEVER TEST")
    print("="*60 + "\n")

    for q in test_queries:
        chunks, status = retrieve(q)
        if status == "OK":
            print(f"   Top match: {chunks[0]['subject']}/{chunks[0]['chapter']}")
            print(f"   Preview: \"{chunks[0]['text'][:120]}...\"\n")
        else:
            print(f"   → Bot would say: 'I don't have reliable notes on this.'\n")
        print("-"*60)