from langgraph.types import Command

from backend.agent.buyer.agent import buyer_agent


initial_state = {
    "request": "I need a laptop under ₹80,000",
    "requirements": {},
    "products": [],
    "recommendation": None,
    "approved": False,
    "policy_result": {},
}

config = {
    "configurable": {
        "thread_id": "buyer-demo-1"
    }
}

result = buyer_agent.invoke(initial_state, config)

print("Approval request:")
print(result["__interrupt__"][0].value)

approval = input("Approve purchase? (yes/no): ").strip().lower()

result = buyer_agent.invoke(
    Command(resume=approval == "yes"),
    config,
)

print("\nFinal result:")
print(result)