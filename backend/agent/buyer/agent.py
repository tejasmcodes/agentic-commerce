from langgraph.graph import StateGraph, START, END
from agent.buyer.utils.state import AgentState
from agent.buyer.utils.nodes import understand_request, search_catalog, recommend_product

graph = StateGraph(AgentState)

graph.add_node("understand_request", understand_request)
graph.add_node("search_catalog", search_catalog)
graph.add_node("recommend_product", recommend_product)

graph.add_edge(START, "understand_request")
graph.add_edge("understand_request","search_catalog")
graph.add_edge("search_catalog","recommend_product")
graph.add_edge("recommend_product", END)

buyer_agent = graph.compile()