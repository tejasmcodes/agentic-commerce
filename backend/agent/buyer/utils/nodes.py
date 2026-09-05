from agent.buyer.utils.state import AgentState
from agent.buyer.utils.tools import (
    parse_requirements,
    search_products,
    choose_cheapest_product,
    check_policy,
    create_payment_order,
    write_audit_log
)
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


def policy_check(state: AgentState):
    if not state["approved"]:
        return {
            "policy_result": {
                "allowed": False,
                "reason": "User did not approve the purchase.",
            }
        }

    recommendation = state["recommendation"]

    if recommendation is None:
        return {
            "policy_result": {
                "allowed": False,
                "reason": "No product was recommended.",
            }
        }

    result = check_policy(
        recommendation,
        state["requirements"],
    )

    return {
        "policy_result": result
    }

def create_payment(state: AgentState):
    if not state["approved"]:
        return {
            "policy_result": {
                "allowed": False,
                "reason": "Payment blocked: user did not approve.",
            }
        }

    if not state["policy_result"].get("allowed"):
        return {
            "policy_result": state["policy_result"]
        }

    recommendation = state["recommendation"]

    if recommendation is None:
        return {
            "policy_result": {
                "allowed": False,
                "reason": "Payment blocked: no recommendation.",
            }
        }

    try:
        order = create_payment_order(recommendation)

        return {
            "policy_result": {
                **state["policy_result"],
                "payment": order,
            }
        }

    except Exception as e:
        return {
            "policy_result": {
                **state["policy_result"],
                "payment": {
                    "status": "failed",
                    "reason": str(e),
                },
            }
        }


def audit_transaction(state: AgentState):
    recommendation = state["recommendation"]
    payment = state["policy_result"].get("payment")

    write_audit_log({
        "request": state["request"],
        "product_id": recommendation["id"] if recommendation else None,
        "product_name": recommendation["name"] if recommendation else None,
        "amount": recommendation["price"] if recommendation else None,
        "currency": recommendation["currency"] if recommendation else None,
        "approved": state["approved"],
        "policy": state["policy_result"],
        "payment": payment,
        "status": (
            "success"
            if payment and payment.get("status") == "created"
            else "rejected"
            if not state["approved"]
            else "policy_blocked"
        ),
    })

    return {}