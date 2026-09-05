from langgraph.graph import StateGraph, START, END

from agent.buyer.utils.state import AgentState
from agent.buyer.utils.nodes import (
    understand_request,
    search_catalog,
    recommend_product,
    approval,
    policy_check,
    create_payment,
)
from langgraph.checkpoint.memory import MemorySaver

graph = StateGraph(AgentState)

graph.add_node("understand_request", understand_request)
graph.add_node("search_catalog", search_catalog)
graph.add_node("recommend_product", recommend_product)
graph.add_node("approval", approval)
graph.add_node("policy_check", policy_check)
graph.add_node("create_payment", create_payment)

graph.add_edge(START, "understand_request")
graph.add_edge("understand_request", "search_catalog")
graph.add_edge("search_catalog", "recommend_product")
graph.add_edge("recommend_product", "approval")
graph.add_conditional_edges(
    "approval",
    lambda state: "policy_check" if state["approved"] else "rejected",
    {
        "policy_check": "policy_check",
        "rejected": END,
    },
)

graph.add_conditional_edges(
    "policy_check",
    lambda state: (
        "create_payment"
        if state["policy_result"].get("allowed")
        else "rejected"
    ),
    {
        "create_payment": "create_payment",
        "rejected": END,
    },
)

graph.add_edge("create_payment", END)

checkpointer = MemorySaver()

buyer_agent = graph.compile(checkpointer=checkpointer)