# backend/scripts/rag_golden_set.py
"""
Golden set for retrieval evaluation of search_medical_knowledge() -
same methodology as the Week 2 Day 4 assignment (precision@k, recall@k,
MRR, nDCG@k on a hand-labelled query set, unanswerable queries included).

Each chunk in the knowledge base is one "---"-separated section, so
relevance is labelled with a short phrase that appears verbatim in
exactly one chunk (verified against both source files) rather than a
chunk ID - IDs are random UUIDs regenerated on every ingest run, but
these phrases stay stable as long as the source .md files don't change.

relevant_markers: [] means the query is intentionally unanswerable from
this knowledge base (nothing in it should score as a confident match).
"""

GOLDEN_SET = [
    {"query": "What should I do for a mild fever at home?", "relevant_markers": ["temporary rise in body temperature"]},
    {"query": "When is a headache a medical emergency?", "relevant_markers": ["the worst headache of your life"]},
    {"query": "How long does a normal cough or cold usually last?", "relevant_markers": ["cough and cold symptoms"]},
    {"query": "When should I worry about stomach pain or nausea?", "relevant_markers": ["occasional nausea, mild stomach pain"]},
    {"query": "What can cause ongoing tiredness?", "relevant_markers": ["ongoing tiredness can have many causes"]},
    {"query": "What does a CBC blood test check for?", "relevant_markers": ["complete blood count"]},
    {"query": "What is the difference between a blood glucose test and HbA1c?", "relevant_markers": ["reflects average\nblood sugar"]},
    {"query": "What does a lipid profile measure?", "relevant_markers": ["cholesterol and triglyceride"]},
    {"query": "What's the difference between an X-ray, CT scan, and MRI?", "relevant_markers": ["x-ray, ultrasound, ct, and mri"]},
    {"query": "Do I need to fast before a blood test?", "relevant_markers": ["8-12 hours"]},
    {"query": "What should I do to prepare for an imaging scan?", "relevant_markers": ["before an imaging scan"]},
    {"query": "What should I expect before a minor surgery or procedure?", "relevant_markers": ["before a procedure or minor surgery"]},
    {"query": "What should I bring to my doctor's appointment?", "relevant_markers": ["appointment preparation"]},
    {"query": "How much sleep should an adult get for good health?", "relevant_markers": ["7-9 hours"]},
    {"query": "Should I keep track of my symptoms between visits?", "relevant_markers": ["symptom log"]},
    {"query": "What is paracetamol used for?", "relevant_markers": ["paracetamol / acetaminophen"]},
    {"query": "What are the precautions for taking ibuprofen?", "relevant_markers": ["ibuprofen (nsaid)"]},
    {"query": "Can I take amoxicillin if I'm allergic to penicillin?", "relevant_markers": ["amoxicillin (antibiotic)"]},
    {"query": "How should metformin be taken to reduce stomach upset?", "relevant_markers": ["metformin"]},
    {"query": "What are common side effects of amlodipine?", "relevant_markers": ["amlodipine"]},
    {"query": "What is omeprazole prescribed for?", "relevant_markers": ["omeprazole (acid reducer)"]},
    {"query": "Does cetirizine cause drowsiness?", "relevant_markers": ["cetirizine / loratadine"]},
    {"query": "What should I do if I miss a dose of my medication?", "relevant_markers": ["if a dose is missed"]},
    # Unanswerable - nothing in the knowledge base covers these
    {"query": "How much does an MRI scan cost at this hospital?", "relevant_markers": []},
    {"query": "What is the recovery timeline after a knee replacement surgery?", "relevant_markers": []},
]