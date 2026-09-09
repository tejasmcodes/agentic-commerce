from langgraph.types import Command

from .agent import build_merchant_graph


def main():
    graph = build_merchant_graph()

    initial_state = {
        "opportunity": None,
        "campaign": None,
        "approved": False,
    }

    config = {
        "configurable": {
            "thread_id": "merchant-demo-1",
        }
    }

    result = graph.invoke(initial_state, config)

    print("\n=== MERCHANT AGENT ===\n")

    print("Revenue opportunity detected:")
    print(result["__interrupt__"][0].value["message"])

    campaign = result["__interrupt__"][0].value["campaign"]

    print(f"\nCampaign: {campaign['name']}")
    print(
        f"{campaign['source_category']} → "
        f"{campaign['target_category']}"
    )
    print(f"Offer: {campaign['offer']}")
    print(f"Reason: {campaign['reason']}")

    response = input("\nApprove campaign? (yes/no): ").strip().lower()

    result = graph.invoke(
        Command(resume=response),
        config,
    )

    if result.get("approved"):
        print("\n✓ Campaign approved")
        print("✓ Campaign created")
        print(f"Status: {result['campaign']['status']}")
    else:
        print("\n✗ Campaign rejected")


if __name__ == "__main__":
    main()