# EVAL.md — CareBridge RAG Retrieval Evaluation

## Scope

Evaluates search_medical_knowledge() — the retrieval step behind the
patient assistant's general_question intent. Corpus: 17 hand-written
sections (~19 chunks after splitting) across two hospital-approved
knowledge files (medical_education.md, medication_information.md).

## Method

Hand-implemented (no eval framework), same approach as the Week 2 Day 4
retrieval-eval assignment:

- *Golden set:* 23 answerable queries (one labelled-relevant chunk
  each, identified by a unique phrase verified to appear in exactly one
  chunk) + 2 unanswerable queries (topics absent from the corpus).
- *Metrics:* Precision@k, Recall@k, MRR, nDCG@k — computed per query,
  then averaged over the answerable set.
- *Stack:* Jina embeddings (jina-embeddings-v3, retrieval.passage /
  retrieval.query tasks) + Qdrant Cloud (cosine similarity, dense
  retrieval only — no hybrid/BM25 or reranking yet).

## Baseline results (dense retrieval only, top_k=4 — the app's default before tuning)

search_medical_knowledge()'s default was top_k=4 at the time this
evaluation started, so the baseline measures retrieval quality at that
value:


Precision@4: 0.250
Recall@4:    1.000
MRR:         0.957
nDCG@4:      0.968


Unanswerable queries (measured at top_k=5, since the score of the
top-ranked chunk doesn't depend on k):


How much does an MRI scan cost at this hospital?        top_score=0.261
What is the recovery timeline after a knee replacement  top_score=0.250


For comparison, the answerable set's top_score ranged roughly 0.31-0.70
(most in the 0.45-0.65 range) — noticeably higher than either
unanswerable query's 0.25-0.26.

## Observations

- *Recall@4 = 1.0*: dense retrieval never failed to surface the
  correct chunk within the top 4, even with a small (~19-chunk) corpus.
- *MRR/nDCG near 1.0 but not exactly 1.0*: 21 of 23 queries retrieved
  the correct chunk at rank 1. Two queries — "How long does a normal
  cough or cold usually last?" and "When should I worry about stomach
  pain or nausea?" — retrieved the correct chunk at rank 2 instead of
  rank 1 (reciprocal rank 0.50 each), likely because both symptom
  descriptions ("Cough and Cold Symptoms", "Stomach Upset") are worded
  close to a neighboring symptom section in the same chunk, causing a
  near-tie in cosine similarity with an adjacent chunk. Not a failure,
  just a ranking tie worth watching as the corpus grows.
- *Precision drops as k grows*: expected, not a retrieval weakness —
  each query has exactly one relevant chunk in the corpus, so
  1 relevant / k retrieved falls as k rises regardless of retrieval
  quality. Precision will only become a meaningful signal once multiple
  chunks can legitimately answer the same query (i.e. once real patient
  documents are ingested in Phase 7).
- **Unanswerable queries scored lower (0.25-0.26) than the answerable
  average**, which is the desired behavior — the system's own
  confidence signal drops for out-of-scope questions rather than
  confidently retrieving an unrelated chunk. It's still not a hard
  cutoff: the system currently always returns top-k regardless of
  score, so a low-confidence chunk can still get passed to the LLM.

## Retrieval count (top_k) tuning: changed from 4 to 2

The baseline top_k=4 wasn't chosen from evidence — it was just the
value already in the code. Swept top_k from 1 to 10 against the same
23-query golden set to check whether a different value performs better.

| k  | Precision@k | Recall@k | MRR@k | nDCG@k |
|----|-------------|----------|-------|--------|
| 1  | 0.913       | 0.913    | 0.913 | 0.913  |
| 2  | 0.500       | 1.000    | 0.957 | 0.968  |
| 3  | 0.333       | 1.000    | 0.957 | 0.968  |
| 4  | 0.250       | 1.000    | 0.957 | 0.968  |
| 5  | 0.200       | 1.000    | 0.957 | 0.968  |
| 7  | 0.143       | 1.000    | 0.957 | 0.968  |
| 10 | 0.100       | 1.000    | 0.957 | 0.968  |

*Decision: top_k = 2.*

Recall, MRR, and nDCG all reach their maximum at k=2 and stay exactly
flat for every larger k tested, including the old default of 4 —
retrieving more than 2 chunks adds no queries that were previously
missed. Precision keeps falling as k grows purely because the
denominator grows while the numerator (relevant chunks found) is capped
at 1 per query in this corpus, so precision alone would wrongly favor
k=1. k=1 is rejected despite its higher precision because it still
misses ~9% of queries (0.913 recall) — the two queries noted above that
ranked the correct chunk second. k=2 is the smallest value that
recovers those without adding chunks that don't help — and, compared
to the old default of 4, sends the LLM two fewer irrelevant chunks per
query at no cost to retrieval quality.

app/services/rag_service.py updated: search_medical_knowledge()'s
default changed from top_k=4 to top_k=2.

*Caveat:* this value is tuned against a small, single-topic-per-chunk
corpus (17 sections). Once Phase 7 ingests real, more heterogeneous
patient/doctor documents — where a query may legitimately have several
relevant chunks — top_k should be re-evaluated against a golden set
built from that larger corpus.

## Next improvements (not yet implemented)

- A minimum-score threshold on retrieval, so clearly out-of-scope
  queries (score below ~0.3) skip RAG grounding entirely and the
  assistant says it doesn't have that information, instead of grounding
  on a weak match
- Query rewriting (Groq) before embedding, for vaguer patient phrasing
- Hybrid dense + keyword search, since exact drug names (e.g.
  "amlodipine") are better served by exact-match than pure dense
  similarity
- Cross-encoder reranking once the corpus grows past a handful of files
-