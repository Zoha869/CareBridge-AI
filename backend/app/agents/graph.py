"""
Builds the patient assistant's LangGraph workflow, described in the
project proposal's Section 12 (Intent -> Context -> Safety -> Route).
"""

from langgraph.graph import StateGraph, END
from app.agents.state import PatientState
from app.agents.nodes import (
    retrieve_context_node,
    intent_node,
    safety_check_node,
    general_response_node,
    patient_history_node,
    new_concern_node,
    appointment_node,
    route_by_intent,
)

builder = StateGraph(PatientState)

builder.add_node("retrieve_context", retrieve_context_node)
builder.add_node("detect_intent", intent_node)
builder.add_node("safety_check", safety_check_node)
builder.add_node("general", general_response_node)
builder.add_node("history", patient_history_node)
builder.add_node("concern", new_concern_node)
builder.add_node("appointment", appointment_node)

builder.set_entry_point("retrieve_context")
builder.add_edge("retrieve_context", "detect_intent")
builder.add_edge("detect_intent", "safety_check")

builder.add_conditional_edges(
    "safety_check",
    route_by_intent,
    {
        "general": "general",
        "history": "history",
        "concern": "concern",
        "appointment": "appointment",
        "end": END,
    },
)

builder.add_edge("general", END)
builder.add_edge("history", END)
builder.add_edge("concern", END)
builder.add_edge("appointment", END)

patient_graph = builder.compile()