from typing import TypedDict

class AgentState(TypedDict):
    request:    str
    requirements:   dict
    products:   list
    recommendation: dict
    approved:   bool
    policy_result:  dict