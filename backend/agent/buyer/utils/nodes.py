from agent.buyer.utils.state import AgentState
from agent.buyer.utils.tools import parse_requirements,search_products, choose_cheapest_product


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

def recommend_product(state: AgentState):
    products = state["products"]
    recommend_product = choose_cheapest_product(products)
    return {
        "recommendation":recommend_product
    }