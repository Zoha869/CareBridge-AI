# backend/scripts/eval_rag_sweep.py
"""
Runs the same retrieval metrics as eval_rag.py across several top_k
values, so top_k is picked from evidence instead of guessed. Answers
the question: how many chunks should search_medical_knowledge() (and
therefore general_response_node's RAG context) actually retrieve?

Usage (from backend/, venv active):
    python -m scripts.eval_rag_sweep
"""

import math
from app.services.rag_service import search_medical_knowledge
from scripts.rag_golden_set import GOLDEN_SET

K_VALUES = [1, 2, 3, 4, 5, 7, 10]
MAX_K = max(K_VALUES)  # fetch once at the largest k, slice down for each k


def is_relevant(chunk_text: str, markers: list[str]) -> bool:
    text = chunk_text.lower()
    return any(marker.lower() in text for marker in markers)


def precision_at_k(hits: list[bool], k: int) -> float:
    return sum(hits[:k]) / k


def recall_at_k(hits: list[bool], k: int, total_relevant: int) -> float:
    return sum(hits[:k]) / total_relevant if total_relevant else 0.0


def reciprocal_rank_at_k(hits: list[bool], k: int) -> float:
    for i, hit in enumerate(hits[:k], start=1):
        if hit:
            return 1.0 / i
    return 0.0


def ndcg_at_k(hits: list[bool], k: int, total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    dcg = sum(hit / math.log2(i + 1) for i, hit in enumerate(hits[:k], start=1))
    ideal_hits = [1] * min(total_relevant, k) + [0] * max(0, k - total_relevant)
    idcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(ideal_hits, start=1))
    return dcg / idcg if idcg > 0 else 0.0


def main():
    # One retrieval per query at MAX_K, reused for every smaller k - avoids
    # re-querying Qdrant/Jina once per k value.
    per_query_hits = []
    for item in GOLDEN_SET:
        if not item["relevant_markers"]:
            continue  # unanswerable queries aren't part of this sweep
        results = search_medical_knowledge(item["query"], top_k=MAX_K)
        hits = [is_relevant(r["text"], item["relevant_markers"]) for r in results]
        per_query_hits.append(hits)

    n = len(per_query_hits)
    print(f"Sweeping top_k over {K_VALUES} on {n} answerable queries\n")
    print(f"{'k':>3s} {'Precision@k':>12s} {'Recall@k':>10s} {'MRR@k':>7s} {'nDCG@k':>8s}")
    for k in K_VALUES:
        p = sum(precision_at_k(h, k) for h in per_query_hits) / n
        r = sum(recall_at_k(h, k, 1) for h in per_query_hits) / n
        mrr = sum(reciprocal_rank_at_k(h, k) for h in per_query_hits) / n
        ndcg = sum(ndcg_at_k(h, k, 1) for h in per_query_hits) / n
        print(f"{k:>3d} {p:>12.3f} {r:>10.3f} {mrr:>7.3f} {ndcg:>8.3f}")

    print("\nPick the smallest k where Recall/MRR/nDCG plateau - going higher")
    print("only adds noisier, lower-relevance chunks into the LLM's context")
    print("without improving whether the right chunk was found.")


if __name__ == "__main__":
    main()