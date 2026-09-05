from agent.buyer.utils.state import Requirements, Product
import re
import os
import razorpay
import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = Path("audit_log.json")

CATALOG = [
        {
            "id": "laptop-001",
            "name": "DevBook Pro",
            "category": "laptop",
            "price": 72000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "laptop-002",
            "name": "CodeMaster 14",
            "category": "laptop",
            "price": 78000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "laptop-003",
            "name": "UltraWork X1",
            "category": "laptop",
            "price": 85000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "laptop-004",
            "name": "ThinkPro 16",
            "category": "laptop",
            "price": 68000,
            "currency": "INR",
            "available": False,
        },
        {
            "id": "phone-001",
            "name": "PixelMax 9",
            "category": "phone",
            "price": 55000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "phone-002",
            "name": "Galaxy Nova",
            "category": "phone",
            "price": 42000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "phone-003",
            "name": "BudgetPhone X",
            "category": "phone",
            "price": 18000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "shoe-001",
            "name": "RunFast Pro",
            "category": "running_shoe",
            "price": 8000,
            "currency": "INR",
            "available": True,
        },
        {
            "id": "shoe-002",
            "name": "TrailRunner X",
            "category": "running_shoe",
            "price": 12000,
            "currency": "INR",
            "available": True,
        },
    ]

CATEGORIES = ["phone","laptop","running_shoe"]

def parse_requirements(request: str) -> Requirements:
    pattern = r'(₹|Rs\.?|INR|\$)\s?(\d[\d,]*)'
    match = re.search(pattern, request)
    currency, price = None, None
    if match:
        currency = "INR" if match.group(1) == "₹" else match.group(1)
        price = int(match.group(2).replace(",", ""))
    category = None
    words = request.split()
    for word in words:
        if word.lower() in CATEGORIES:
            category = word.lower()

    requirements = {"category": category,
            "price": price,
            "currency": currency}
    
    return requirements
            
        

def search_products(requirements: Requirements) -> list[Product]:
    products=[]
    required_category = requirements["category"]
    max_price = requirements["price"]
    required_currency = requirements["currency"]
    for product in CATALOG:
        if( product["category"] == required_category
        and product["currency"] == required_currency
        and product["price"] <= max_price
        and product["available"] == True):
            products.append(product)

    return products

def choose_cheapest_product(products: list[Product]) -> Product | None:
    if not products:
        return None

    min_price = products[0]["price"]
    recommended = products[0]

    for product in products:
        if product["price"] < min_price:
            min_price = product["price"]
            recommended = product

    return recommended

def check_policy(product: Product, requirements: Requirements) -> dict:
    if product["price"] > requirements["price"]:
        return {
            "allowed": False,
            "reason": "Product exceeds the user's budget.",
        }

    if product["currency"] != requirements["currency"]:
        return {
            "allowed": False,
            "reason": "Currency mismatch.",
        }

    if not product["available"]:
        return {
            "allowed": False,
            "reason": "Product is unavailable.",
        }

    return {
        "allowed": True,
        "reason": "All policy checks passed.",
    }

def create_payment_order(product: Product) -> dict:
    client = razorpay.Client(
        auth=(
            os.environ["RAZORPAY_KEY_ID"],
            os.environ["RAZORPAY_KEY_SECRET"],
        )
    )

    order = client.order.create({
        "amount": product["price"] * 100,
        "currency": product["currency"],
        "receipt": f"receipt_{product['id']}",
    })

    return {
        "order_id": order["id"],
        "status": order["status"],
        "amount": order["amount"],
        "currency": order["currency"],
    }


def write_audit_log(entry: dict) -> None:
    logs = []

    if AUDIT_FILE.exists():
        with open(AUDIT_FILE, "r") as f:
            logs = json.load(f)

    logs.append({
        **entry,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    with open(AUDIT_FILE, "w") as f:
        json.dump(logs, f, indent=2)