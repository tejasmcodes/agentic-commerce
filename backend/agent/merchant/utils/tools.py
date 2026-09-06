import json
import os
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI

from .state import MerchantCampaign, MerchantOpportunity

AUDIT_FILE = Path(__file__).resolve().parents[3] / "merchant_audit_log.json"

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
)

def detect_opportunity_with_llm(catalog: list[dict]) -> MerchantOpportunity:
    prompt = f"""
        You are an AI growth strategist for an ecommerce merchant.

        Analyze the merchant's product catalog and identify the single strongest
        cross-sell opportunity.

        Catalog:
        {json.dumps(catalog, indent=2)}

        Rules:
        - Choose a source category that has products customers are likely to buy.
        - Choose a complementary target category that could naturally be purchased
        with the source category.
        - Both categories MUST exist in the catalog.
        - Prefer opportunities that can increase average order value.
        - Do not invent products or categories.
        - Return a concise explanation of why this is a strong opportunity.
        - Return only the structured result.
        """

    structured_llm = llm.with_structured_output(MerchantOpportunity)
    opportunity = structured_llm.invoke(prompt)

    valid_categories = {
        product["category"]
        for product in catalog
    }

    if (
        opportunity.source_category not in valid_categories
        or opportunity.target_category not in valid_categories
    ):
        raise ValueError(
            "LLM returned an opportunity with categories not present in the catalog"
        )

    return opportunity


def generate_campaign_with_llm(
    opportunity: MerchantOpportunity,
    catalog: list[dict],
) -> MerchantCampaign:
    prompt = f"""
You are an AI growth strategist for an ecommerce merchant.

Create a concrete cross-sell campaign based on this opportunity.

Opportunity:
{opportunity.model_dump_json(indent=2)}

Relevant catalog:
{json.dumps(catalog, indent=2)}

Rules:
- Create one practical campaign.
- The source category and target category MUST exactly match the opportunity.
- The offer must be easy for a merchant to understand and execute.
- Focus on increasing average order value.
- Do not invent products or categories.
- Give the campaign a concise, compelling name.
- Return a concise explanation of the business rationale.
- Return only the structured result.
"""

    structured_llm = llm.with_structured_output(MerchantCampaign)

    return structured_llm.invoke(prompt)


def write_merchant_audit_log(entry: dict) -> None:
    """Write a merchant campaign audit entry."""

    logs = []

    if AUDIT_FILE.exists() and AUDIT_FILE.stat().st_size > 0:
        try:
            with open(AUDIT_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(entry)

    with open(AUDIT_FILE, "w") as f:
        json.dump(logs, f, indent=2)