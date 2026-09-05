from typing import TypedDict


class MerchantState(TypedDict):
    opportunity: dict | None
    campaign: dict | None
    approved: bool