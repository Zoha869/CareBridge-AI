# backend/scripts/eval_rag.py
"""
Retrieval evaluation for search_medical_knowledge() - same
hand-implemented metrics as the Week 2 Day 4 assignment (no eval
framework), run against the golden set in rag_golden_set.py.

Usage (from backend/, venv active):
    python -m scripts.eval_rag
"""

import math
from app.services.rag_service import search_medical_knowledge
from scripts.rag_golden_set import GOLDEN_SET

TOP_K = 5


def is_relevant(chunk_text: str, markers: list[str]) -> bool:
    text = chunk_text.lower()
    return any(marker.lower() in text for marker in markers)


def precision_at_k(hits: list[bool], k: int) -> float:
    return sum(hits[:k]) / k


def recall_at_k(hits: list[bool], k: int, total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    return sum(hits[:k]) / total_relevant


def reciprocal_rank(hits: list[bool]) -> float:
    for i, hit in enumerate(hits, start=1):
        if hit:
            return 1.0 / i
    return 0.0


def ndcg_at_k(hits: list[bool], k: int, total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    dcg = sum(hit / math.log2(i + 1) for i, hit in enumerate(hits[:k], start=1))
    # Ideal ranking: all relevant chunks packed at the top (only ever 1 here)
    ideal_hits = [1] * min(total_relevant, k) + [0] * max(0, k - total_relevant)
    idcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(ideal_hits, start=1))
    return dcg / idcg if idcg > 0 else 0.0


def main():
    answerable_rows = []
    unanswerable_rows = []

    for item in GOLDEN_SET:
        query, markers = item["query"], item["relevant_markers"]
        results = search_medical_knowledge(query, top_k=TOP_K)
        hits = [is_relevant(r["text"], markers) for r in results]
        top_score = results[0]["score"] if results else 0.0

        if markers:
            total_relevant = 1  # every answerable query maps to exactly one chunk
            answerable_rows.append({
                "query": query,
                "p@5": precision_at_k(hits, TOP_K),
                "r@5": recall_at_k(hits, TOP_K, total_relevant),
                "mrr": reciprocal_rank(hits),
                "ndcg@5": ndcg_at_k(hits, TOP_K, total_relevant),
                "top_score": top_score,
            })
        else:
            unanswerable_rows.append({"query": query, "top_score": top_score})

    print(f"\n=== Answerable queries ({len(answerable_rows)}) ===")
    print(f"{'query':55s} {'P@5':>5s} {'R@5':>5s} {'MRR':>5s} {'nDCG@5':>7s} {'top_score':>9s}")
    for row in answerable_rows:
        print(f"{row['query'][:55]:55s} {row['p@5']:.2f}  {row['r@5']:.2f}  {row['mrr']:.2f}  "
              f"{row['ndcg@5']:.3f}   {row['top_score']:.3f}")

    n = len(answerable_rows)
    print("\n--- Averages over answerable queries ---")
    print(f"Precision@5: {sum(r['p@5'] for r in answerable_rows) / n:.3f}")
    print(f"Recall@5:    {sum(r['r@5'] for r in answerable_rows) / n:.3f}")
    print(f"MRR:         {sum(r['mrr'] for r in answerable_rows) / n:.3f}")
    print(f"nDCG@5:      {sum(r['ndcg@5'] for r in answerable_rows) / n:.3f}")

    print(f"\n=== Unanswerable queries ({len(unanswerable_rows)}) ===")
    print("(no relevant chunk exists in the KB - watch for high top_score, which")
    print(" would mean the system might confidently answer from an unrelated chunk)")
    for row in unanswerable_rows:
        print(f"{row['query'][:55]:55s} top_score={row['top_score']:.3f}")


if __name__ == "__main__":
    main()