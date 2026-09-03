from agent.buyer.utils.state import AgentState
from agent.buyer.utils.tools import parse_requirements,search_products


def understand_request(state: AgentState):
    request = state["request"]
    requirements = parse_requirements(request)
    return {
        "requirements": requirements
    }

def search_catalog(state: AgentState):
    requirements = state["requirements"]
    products = search_products(requirements)
    return{
        "products": products
    }