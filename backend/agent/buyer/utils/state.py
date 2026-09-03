from typing import TypedDict
class Requirements(TypedDict):
    category:   str
    price:  int
    currency:   str

class Product(TypedDict):
    id: str
    name: str
    category: str
    price: int
    currency: str
    available: bool

class AgentState(TypedDict):
    request:    str
    requirements:   Requirements
    products:   list[Product]
    recommendation: Product | None
    approved:   bool
    policy_result:  dict