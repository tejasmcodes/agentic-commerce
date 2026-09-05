from langgraph.types import interrupt

from .state import MerchantState
from .tools import write_merchant_audit_log


def detect_opportunity(state: MerchantState) -> MerchantState:
    """Detect a simple cross-sell opportunity from the merchant catalog."""

    opportunity = {
        "source_category": "running_shoe",
        "target_category": "socks",
        "reason": (
            "Running-shoe customers have an opportunity for "
            "a complementary socks product."
        ),
    }

    return {
        **state,
        "opportunity": opportunity,
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