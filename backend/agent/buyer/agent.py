from langgraph.graph import StateGraph, START, END

from agent.buyer.utils.state import AgentState
from agent.buyer.utils.nodes import (
    understand_request,
    search_catalog,
    recommend_product,
    approval,
    policy_check,
    create_payment,
    audit_transaction
)
from langgraph.checkpoint.memory import MemorySaver

graph = StateGraph(AgentState)

graph.add_node("understand_request", understand_request)
graph.add_node("search_catalog", search_catalog)
graph.add_node("recommend_product", recommend_product)
graph.add_node("approval", approval)
graph.add_node("policy_check", policy_check)
graph.add_node("create_payment", create_payment)
graph.add_node("audit_transaction", audit_transaction)

graph.add_edge(START, "understand_request")
graph.add_edge("understand_request", "search_catalog")
graph.add_edge("search_catalog", "recommend_product")
graph.add_edge("recommend_product", "approval")
graph.add_conditional_edges(
    "approval",
    lambda state: "policy_check" if state["approved"] else "audit_transaction",
    {
        "policy_check": "policy_check",
        "audit_transaction": "audit_transaction",
    },
)

graph.add_conditional_edges(
    "policy_check",
    lambda state: (
        "create_payment"
        if state["policy_result"].get("allowed")
        else "audit_transaction"
    ),
    {
        "create_payment": "create_payment",
        "audit_transaction": "audit_transaction",
    },
)

graph.add_edge("create_payment", "audit_transaction")
graph.add_edge("audit_transaction", END)

checkpointer = MemorySaver()

buyer_agent = graph.compile(checkpointer=checkpointer)