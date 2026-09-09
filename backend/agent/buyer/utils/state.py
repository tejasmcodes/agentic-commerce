from typing import TypedDict
from pydantic import BaseModel

class RequirementExtraction(BaseModel):
    category: str | None = None
    price: int | None = None
    currency: str | None = None


class ProductRecommendation(BaseModel):
    product_id: str
    reason: str

class Requirements(TypedDict):
    category:   str | None
    price:  int | None
    currency:   str | None

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