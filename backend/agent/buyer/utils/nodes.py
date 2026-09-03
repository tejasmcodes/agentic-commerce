from agent.buyer.utils.state import AgentState
from agent.buyer.utils.tools import search_products
import re

def understand_request(state: AgentState):
    categories = ["phone","laptop","running_shoe"]
    request = state["request"]
    pattern = r'(₹|Rs\.?|INR|\$)\s?(\d[\d,]*)'
    match = re.search(pattern, request)
    currency, price = None, None
    if match:
        currency = "INR" if match.group(1) == "₹" else match.group(1)
        price = int(match.group(2).replace(",", ""))
    category = None
    words = request.split()
    for word in words:
        if word.lower() in categories:
            category = word.lower()
    return {
        "requirements":{
            "category": category,
            "price": price,
            "currency": currency
        }
    }

def search_catalog(state: AgentState):
    requirements = state["requirements"]
    products = search_products(requirements)
    return{
        "products": products
    }