from langgraph.types import interrupt

from .state import MerchantOpportunity, MerchantState
from .tools import (
    detect_opportunity_with_llm,
    generate_campaign_with_llm,
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
    opportunity = state["opportunity"]

    campaign = generate_campaign_with_llm(
    MerchantOpportunity(**opportunity),
    CATALOG,
    )

    return {
        **state,
        "campaign": campaign.model_dump(),
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