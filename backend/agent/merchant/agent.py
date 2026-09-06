from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .utils.state import MerchantState
from .utils.nodes import (
    detect_opportunity,
    generate_campaign,
    approval,
    create_campaign,
    audit_campaign,
)


def build_merchant_graph():
    graph = StateGraph(MerchantState)

    graph.add_node("detect_opportunity", detect_opportunity)
    graph.add_node("generate_campaign", generate_campaign)
    graph.add_node("approval", approval)
    graph.add_node("create_campaign", create_campaign)
    graph.add_node("audit_campaign", audit_campaign)

    graph.set_entry_point("detect_opportunity")

    graph.add_edge("detect_opportunity", "generate_campaign")
    graph.add_edge("generate_campaign", "approval")

    graph.add_conditional_edges(
        "approval",
        lambda state: (
            "create_campaign"
            if state["approved"]
            else "audit_campaign"
        ),
        {
            "create_campaign": "create_campaign",
            "audit_campaign": "audit_campaign",
        },
    )

    graph.add_edge("create_campaign", "audit_campaign")
    graph.add_edge("audit_campaign", END)

    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)

merchant_agent = build_merchant_graph()