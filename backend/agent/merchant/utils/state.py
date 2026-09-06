from typing import TypedDict

from pydantic import BaseModel


class MerchantOpportunity(BaseModel):
    source_category: str
    target_category: str
    reason: str


class MerchantCampaign(BaseModel):
    name: str
    source_category: str
    target_category: str
    offer: str
    reason: str


class MerchantState(TypedDict):
    opportunity: dict | None
    campaign: dict | None
    approved: bool