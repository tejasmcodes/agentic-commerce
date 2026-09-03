from agent.buyer.agent import buyer_agent

initial_state = {
    "request": "I need a laptop under ₹80,000",
    "requirements": {},
    "products": [],
    "recommendation": {},
    "approved": False,
    "policy_result": {},
}

result = buyer_agent.invoke(initial_state)
print(result)