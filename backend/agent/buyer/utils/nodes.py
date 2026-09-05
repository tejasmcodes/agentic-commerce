from agent.buyer.utils.state import AgentState
from agent.buyer.utils.tools import parse_requirements,search_products, choose_cheapest_product
from langgraph.types import interrupt


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
    recommendation  = choose_cheapest_product(products)
    return {
        "recommendation":recommendation 
    }


def approval(state: AgentState):
    recommendation = state["recommendation"]

    if recommendation is None:
        return {
            "approved": False
        }

    user_response = interrupt({
        "message": "Do you approve this purchase?",
        "product": recommendation
    })

    return {
        "approved": bool(user_response)
    }