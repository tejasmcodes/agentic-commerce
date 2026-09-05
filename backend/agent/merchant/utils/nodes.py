from langgraph.types import interrupt

from .state import MerchantState
from .tools import (
    detect_opportunity_with_llm,
    write_merchant_audit_log,
)

from backend.agent.buyer.utils.tools import CATALOG


def detect_opportunity(state: MerchantState) -> MerchantState:
    """Detect a cross-sell opportunity using the merchant catalog."""

    opportunity = detect_opportunity_with_llm(CATALOG)

    return {
        **state,
        "opportunity": opportunity.model_dump(),
    }


def generate_campaign(state: MerchantState) -> MerchantState:
    """Turn the opportunity into a concrete campaign proposal."""

    opportunity = state["opportunity"]

    campaign = {
        "name": "Run Better Bundle",
        "source_category": opportunity["source_category"],
        "target_category": opportunity["target_category"],
        "offer": "10% off socks with running shoes",
        "reason": "Increase average order value through a complementary product.",
    }

    return {
        **state,
        "campaign": campaign,
    }


def approval(state: MerchantState) -> MerchantState:
    """Ask the merchant to explicitly approve the campaign."""

    campaign = state["campaign"]

    response = interrupt(
        {
            "type": "merchant_campaign_approval",
            "campaign": campaign,
            "message": "Approve this campaign?",
        }
    )

    approved = (
        response is True
        or response == "yes"
        or (
            isinstance(response, dict)
            and response.get("approved") is True
        )
    )

    return {
        **state,
        "approved": approved,
    }


def create_campaign(state: MerchantState) -> MerchantState:
    """Create a deterministic campaign record."""

    campaign = state["campaign"]

    campaign_record = {
        **campaign,
        "status": "created",
    }

    return {
        **state,
        "campaign": campaign_record,
    }

def audit_campaign(state: MerchantState) -> MerchantState:
    """Record the merchant campaign decision."""

    campaign = state["campaign"]

    write_merchant_audit_log({
        "type": "merchant_campaign",
        "campaign": campaign,
        "approved": state["approved"],
        "status": (
            "created"
            if state["approved"] and campaign
            else "rejected"
        ),
    })

    return state