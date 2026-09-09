from backend.agent.buyer.utils.state import (
    Requirements,
    Product,
    RequirementExtraction,
    ProductRecommendation,
)
import re
import os
import razorpay
import json
from datetime import datetime, timezone
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
)

AUDIT_FILE = Path(__file__).resolve().parents[3] / "buyer_audit_log.json"

CATALOG = [
    # Laptops
    {
        "id": "laptop-001",
        "name": "DevBook Pro",
        "category": "laptop",
        "price": 72000,
        "currency": "INR",
        "available": True,
        "description": "Developer-focused laptop for software development and productivity.",
        "features": ["16GB RAM", "512GB SSD", "14-inch display", "Intel Core i7"],
        "tags": ["developer", "coding", "productivity"],
    },
    {
        "id": "laptop-002",
        "name": "CodeMaster 14",
        "category": "laptop",
        "price": 78000,
        "currency": "INR",
        "available": True,
        "description": "Performance laptop designed for programmers and engineers.",
        "features": ["16GB RAM", "1TB SSD", "14-inch display", "AMD Ryzen 7"],
        "tags": ["developer", "coding", "performance"],
    },
    {
        "id": "laptop-003",
        "name": "UltraWork X1",
        "category": "laptop",
        "price": 85000,
        "currency": "INR",
        "available": True,
        "description": "Premium productivity laptop with a large high-resolution display.",
        "features": ["16GB RAM", "1TB SSD", "15.6-inch display", "Intel Core i7"],
        "tags": ["productivity", "premium", "office"],
    },
    {
        "id": "laptop-004",
        "name": "ThinkPro 16",
        "category": "laptop",
        "price": 68000,
        "currency": "INR",
        "available": False,
        "description": "Large-screen business laptop for office productivity.",
        "features": ["16GB RAM", "512GB SSD", "16-inch display"],
        "tags": ["business", "office", "productivity"],
    },
    {
        "id": "laptop-005",
        "name": "CreatorBook Air",
        "category": "laptop",
        "price": 92000,
        "currency": "INR",
        "available": True,
        "description": "Lightweight laptop for creators, designers and professionals.",
        "features": ["16GB RAM", "1TB SSD", "14-inch display", "High-resolution screen"],
        "tags": ["creator", "design", "portable", "premium"],
    },

    # Phones
    {
        "id": "phone-001",
        "name": "PixelMax 9",
        "category": "phone",
        "price": 55000,
        "currency": "INR",
        "available": True,
        "description": "Premium smartphone with excellent camera and display.",
        "features": ["12GB RAM", "256GB storage", "50MP camera", "120Hz display"],
        "tags": ["camera", "premium", "photography"],
    },
    {
        "id": "phone-002",
        "name": "Galaxy Nova",
        "category": "phone",
        "price": 42000,
        "currency": "INR",
        "available": True,
        "description": "Balanced smartphone for everyday productivity and entertainment.",
        "features": ["8GB RAM", "256GB storage", "50MP camera", "AMOLED display"],
        "tags": ["productivity", "entertainment", "value"],
    },
    {
        "id": "phone-003",
        "name": "BudgetPhone X",
        "category": "phone",
        "price": 18000,
        "currency": "INR",
        "available": True,
        "description": "Affordable smartphone for everyday communication and apps.",
        "features": ["6GB RAM", "128GB storage", "50MP camera"],
        "tags": ["budget", "value", "everyday"],
    },
    {
        "id": "phone-004",
        "name": "UltraPhone Pro",
        "category": "phone",
        "price": 68000,
        "currency": "INR",
        "available": True,
        "description": "Flagship smartphone built for photography and demanding users.",
        "features": ["16GB RAM", "512GB storage", "108MP camera", "120Hz AMOLED"],
        "tags": ["flagship", "camera", "performance"],
    },
    {
        "id": "phone-005",
        "name": "PowerPhone Max",
        "category": "phone",
        "price": 35000,
        "currency": "INR",
        "available": True,
        "description": "Long-battery-life smartphone for heavy daily use.",
        "features": ["8GB RAM", "256GB storage", "6000mAh battery"],
        "tags": ["battery", "travel", "value"],
    },

    # Running shoes
    {
        "id": "shoe-001",
        "name": "RunFast Pro",
        "category": "running_shoe",
        "price": 8000,
        "currency": "INR",
        "available": True,
        "description": "Lightweight daily running shoe for road runners.",
        "features": ["Cushioned sole", "Breathable mesh", "Lightweight design"],
        "tags": ["running", "road", "lightweight"],
    },
    {
        "id": "shoe-002",
        "name": "TrailRunner X",
        "category": "running_shoe",
        "price": 12000,
        "currency": "INR",
        "available": True,
        "description": "Durable running shoe designed for trails and uneven terrain.",
        "features": ["Trail grip", "Reinforced upper", "Shock absorption"],
        "tags": ["running", "trail", "outdoor"],
    },
    {
        "id": "shoe-003",
        "name": "SprintElite",
        "category": "running_shoe",
        "price": 15000,
        "currency": "INR",
        "available": True,
        "description": "Responsive performance shoe for speed-focused runners.",
        "features": ["Responsive foam", "Lightweight upper", "Race-oriented design"],
        "tags": ["running", "speed", "performance"],
    },
    {
        "id": "shoe-004",
        "name": "ComfortRun 2",
        "category": "running_shoe",
        "price": 6500,
        "currency": "INR",
        "available": True,
        "description": "Comfort-focused running shoe for beginners and casual runners.",
        "features": ["Soft cushioning", "Breathable mesh", "Flexible sole"],
        "tags": ["running", "beginner", "comfort", "budget"],
    },

    # Headphones
    {
        "id": "headphone-001",
        "name": "QuietSound Pro",
        "category": "headphone",
        "price": 14000,
        "currency": "INR",
        "available": True,
        "description": "Wireless noise-cancelling headphones for focused work.",
        "features": ["Active noise cancellation", "40-hour battery", "Bluetooth"],
        "tags": ["noise-cancelling", "work", "travel"],
    },
    {
        "id": "headphone-002",
        "name": "BassBeat X",
        "category": "headphone",
        "price": 9000,
        "currency": "INR",
        "available": True,
        "description": "Wireless headphones with powerful bass for music lovers.",
        "features": ["Deep bass", "30-hour battery", "Bluetooth 5.3"],
        "tags": ["music", "bass", "wireless"],
    },
    {
        "id": "headphone-003",
        "name": "StudioMonitor 1",
        "category": "headphone",
        "price": 18000,
        "currency": "INR",
        "available": True,
        "description": "Studio-style headphones for accurate audio monitoring.",
        "features": ["High-resolution audio", "Detachable cable", "Over-ear design"],
        "tags": ["audio", "studio", "professional"],
    },
    {
        "id": "headphone-004",
        "name": "Everyday Buds",
        "category": "headphone",
        "price": 4500,
        "currency": "INR",
        "available": True,
        "description": "Compact wireless earbuds for everyday listening.",
        "features": ["Wireless", "24-hour case battery", "Compact design"],
        "tags": ["earbuds", "budget", "everyday"],
    },

    # Monitors
    {
        "id": "monitor-001",
        "name": "CodeView 27",
        "category": "monitor",
        "price": 22000,
        "currency": "INR",
        "available": True,
        "description": "27-inch QHD monitor optimized for programming and productivity.",
        "features": ["27-inch", "QHD", "75Hz", "Height adjustable"],
        "tags": ["coding", "developer", "productivity"],
    },
    {
        "id": "monitor-002",
        "name": "UltraWide Work 34",
        "category": "monitor",
        "price": 38000,
        "currency": "INR",
        "available": True,
        "description": "Ultrawide monitor for multitasking and professional workflows.",
        "features": ["34-inch ultrawide", "3440x1440", "100Hz"],
        "tags": ["multitasking", "productivity", "ultrawide"],
    },
    {
        "id": "monitor-003",
        "name": "GameVision 27",
        "category": "monitor",
        "price": 28000,
        "currency": "INR",
        "available": True,
        "description": "High-refresh gaming monitor with smooth motion.",
        "features": ["27-inch", "165Hz", "1ms response", "QHD"],
        "tags": ["gaming", "high-refresh", "performance"],
    },
    {
        "id": "monitor-004",
        "name": "OfficeView 24",
        "category": "monitor",
        "price": 12000,
        "currency": "INR",
        "available": True,
        "description": "Affordable Full HD monitor for office and home use.",
        "features": ["24-inch", "Full HD", "75Hz"],
        "tags": ["office", "budget", "productivity"],
    },

    # Keyboards
    {
        "id": "keyboard-001",
        "name": "CodeKeys Mechanical",
        "category": "keyboard",
        "price": 7500,
        "currency": "INR",
        "available": True,
        "description": "Mechanical keyboard designed for programmers.",
        "features": ["Mechanical switches", "RGB backlight", "USB-C"],
        "tags": ["coding", "developer", "mechanical"],
    },
    {
        "id": "keyboard-002",
        "name": "OfficeType Wireless",
        "category": "keyboard",
        "price": 3500,
        "currency": "INR",
        "available": True,
        "description": "Quiet wireless keyboard for office productivity.",
        "features": ["Wireless", "Low-profile keys", "Long battery"],
        "tags": ["office", "wireless", "quiet"],
    },
    {
        "id": "keyboard-003",
        "name": "ProBoard 75",
        "category": "keyboard",
        "price": 9500,
        "currency": "INR",
        "available": True,
        "description": "Compact premium mechanical keyboard for enthusiasts.",
        "features": ["75% layout", "Hot-swappable switches", "RGB"],
        "tags": ["mechanical", "premium", "compact"],
    },

    # Mice
    {
        "id": "mouse-001",
        "name": "Precision Mouse Pro",
        "category": "mouse",
        "price": 5000,
        "currency": "INR",
        "available": True,
        "description": "Ergonomic wireless mouse for long work sessions.",
        "features": ["Ergonomic design", "Wireless", "Adjustable DPI"],
        "tags": ["productivity", "ergonomic", "wireless"],
    },
    {
        "id": "mouse-002",
        "name": "GameMouse X",
        "category": "mouse",
        "price": 4000,
        "currency": "INR",
        "available": True,
        "description": "Lightweight high-precision mouse for gaming.",
        "features": ["High DPI sensor", "Lightweight", "RGB"],
        "tags": ["gaming", "performance", "lightweight"],
    },
    {
        "id": "mouse-003",
        "name": "TravelMouse Mini",
        "category": "mouse",
        "price": 1800,
        "currency": "INR",
        "available": True,
        "description": "Compact wireless mouse designed for travel.",
        "features": ["Compact", "Wireless", "Silent clicks"],
        "tags": ["travel", "portable", "budget"],
    },

    # Laptop stands
    {
        "id": "stand-001",
        "name": "AluLift Stand",
        "category": "laptop_stand",
        "price": 3500,
        "currency": "INR",
        "available": True,
        "description": "Aluminum laptop stand for improved desk ergonomics.",
        "features": ["Aluminum", "Adjustable height", "Foldable"],
        "tags": ["ergonomic", "laptop", "desk"],
    },
    {
        "id": "stand-002",
        "name": "FoldStand Go",
        "category": "laptop_stand",
        "price": 2200,
        "currency": "INR",
        "available": True,
        "description": "Portable foldable laptop stand for remote workers.",
        "features": ["Foldable", "Lightweight", "Portable"],
        "tags": ["travel", "portable", "remote-work"],
    },
    {
        "id": "stand-003",
        "name": "ProDesk Riser",
        "category": "laptop_stand",
        "price": 5500,
        "currency": "INR",
        "available": True,
        "description": "Heavy-duty adjustable stand for permanent workstations.",
        "features": ["Metal construction", "Height adjustable", "Stable base"],
        "tags": ["office", "ergonomic", "desk"],
    },

    # Backpacks
    {
        "id": "bag-001",
        "name": "TechPack 20L",
        "category": "backpack",
        "price": 4500,
        "currency": "INR",
        "available": True,
        "description": "Laptop backpack with organized compartments for tech gear.",
        "features": ["20L capacity", "Laptop sleeve", "Water resistant"],
        "tags": ["laptop", "travel", "work"],
    },
    {
        "id": "bag-002",
        "name": "UrbanCarry Pro",
        "category": "backpack",
        "price": 6500,
        "currency": "INR",
        "available": True,
        "description": "Premium commuter backpack for professionals.",
        "features": ["25L capacity", "Laptop compartment", "Water resistant"],
        "tags": ["business", "commute", "premium"],
    },
    {
        "id": "bag-003",
        "name": "DayPack Lite",
        "category": "backpack",
        "price": 2500,
        "currency": "INR",
        "available": True,
        "description": "Lightweight everyday backpack for students and commuters.",
        "features": ["18L capacity", "Laptop sleeve", "Lightweight"],
        "tags": ["budget", "student", "everyday"],
    },

    # Chargers
    {
        "id": "charger-001",
        "name": "PowerCharge 65W",
        "category": "charger",
        "price": 2800,
        "currency": "INR",
        "available": True,
        "description": "65W USB-C charger for laptops, phones and tablets.",
        "features": ["65W output", "USB-C PD", "Compact"],
        "tags": ["laptop", "phone", "fast-charging"],
    },
    {
        "id": "charger-002",
        "name": "FastCharge 33W",
        "category": "charger",
        "price": 1500,
        "currency": "INR",
        "available": True,
        "description": "Compact fast charger for smartphones.",
        "features": ["33W output", "USB-C", "Fast charging"],
        "tags": ["phone", "fast-charging", "budget"],
    },
    {
        "id": "charger-003",
        "name": "MultiPort 100W",
        "category": "charger",
        "price": 4500,
        "currency": "INR",
        "available": True,
        "description": "High-power multi-port charger for multiple devices.",
        "features": ["100W output", "3 USB-C ports", "1 USB-A port"],
        "tags": ["multi-device", "laptop", "premium"],
    },

    # Power banks
    {
        "id": "powerbank-001",
        "name": "PowerBank 20K",
        "category": "power_bank",
        "price": 3000,
        "currency": "INR",
        "available": True,
        "description": "High-capacity power bank for travel and heavy phone users.",
        "features": ["20000mAh", "22.5W fast charging", "USB-C"],
        "tags": ["travel", "phone", "battery"],
    },
    {
        "id": "powerbank-002",
        "name": "SlimCharge 10K",
        "category": "power_bank",
        "price": 1800,
        "currency": "INR",
        "available": True,
        "description": "Slim portable power bank for everyday carry.",
        "features": ["10000mAh", "18W charging", "Slim design"],
        "tags": ["portable", "phone", "budget"],
    },
    {
        "id": "powerbank-003",
        "name": "TravelPower 25K",
        "category": "power_bank",
        "price": 4200,
        "currency": "INR",
        "available": True,
        "description": "Large capacity power bank for long trips and travel.",
        "features": ["25000mAh", "65W output", "USB-C PD"],
        "tags": ["travel", "laptop", "high-capacity"],
    },

    # Phone cases
    {
        "id": "case-001",
        "name": "ShieldCase Pro",
        "category": "phone_case",
        "price": 1800,
        "currency": "INR",
        "available": True,
        "description": "Protective premium case with reinforced corners.",
        "features": ["Shock protection", "Raised edges", "Wireless charging compatible"],
        "tags": ["protection", "premium", "phone"],
    },
    {
        "id": "case-002",
        "name": "ClearGuard Case",
        "category": "phone_case",
        "price": 900,
        "currency": "INR",
        "available": True,
        "description": "Slim transparent case for everyday phone protection.",
        "features": ["Transparent", "Slim profile", "Scratch resistant"],
        "tags": ["budget", "slim", "phone"],
    },
    {
        "id": "case-003",
        "name": "ArmorCase Max",
        "category": "phone_case",
        "price": 2200,
        "currency": "INR",
        "available": True,
        "description": "Heavy-duty phone case for maximum drop protection.",
        "features": ["Military-style protection", "Grip texture", "Raised camera protection"],
        "tags": ["rugged", "protection", "outdoor"],
    },

    # Socks for merchant cross-sell
    {
        "id": "sock-001",
        "name": "RunDry Performance Socks",
        "category": "socks",
        "price": 900,
        "currency": "INR",
        "available": True,
        "description": "Moisture-wicking running socks designed for long runs.",
        "features": ["Moisture wicking", "Breathable fabric", "Cushioned sole"],
        "tags": ["running", "sports", "comfort"],
    },
    {
        "id": "sock-002",
        "name": "Everyday Sport Socks",
        "category": "socks",
        "price": 600,
        "currency": "INR",
        "available": True,
        "description": "Comfortable everyday sports socks.",
        "features": ["Cotton blend", "Breathable", "Ankle support"],
        "tags": ["sports", "everyday", "budget"],
    },
    {
        "id": "sock-003",
        "name": "TrailGrip Socks",
        "category": "socks",
        "price": 1200,
        "currency": "INR",
        "available": True,
        "description": "Durable performance socks for trail running.",
        "features": ["Reinforced heel", "Moisture wicking", "Trail cushioning"],
        "tags": ["trail", "running", "outdoor"],
    },
]

CATEGORIES = [
    "laptop",
    "phone",
    "running_shoe",
    "headphone",
    "monitor",
    "keyboard",
    "mouse",
    "laptop_stand",
    "backpack",
    "charger",
    "power_bank",
    "phone_case",
    "socks",
]

def parse_requirements(request: str) -> Requirements:
    prompt = f"""
            You are a shopping requirements extraction assistant.

            Extract the purchase requirements from the user's request.

            Rules:
            - category: identify the product category if stated or clearly implied.
            - price: extract the maximum budget as an integer if the user specifies one.
            - currency: return a three-letter currency code such as INR or USD.
            - If a field is not specified, return null.
            - Do not invent information.
            - Return only the structured result.

            User request:
            {request}
            """

    structured_llm = llm.with_structured_output(RequirementExtraction)

    result = structured_llm.invoke(prompt)

    return {
        "category": result.category,
        "price": result.price,
        "currency": result.currency,
    }
            

def parse_requirements_with_llm(request: str) -> Requirements:
    prompt = f"""
You are a shopping assistant.

Extract the user's purchase requirements from the request below.

Return:
- category: the product category, or null
- price: the maximum budget as an integer, or null
- currency: the currency code, or null

Only extract information explicitly stated or clearly implied by the request.
Do not invent requirements.

User request:
{request}
"""

    structured_llm = llm.with_structured_output(Requirements)

    return structured_llm.invoke(prompt)


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


def recommend_product_with_llm(
    request: str,
    requirements: Requirements,
    products: list[Product],
) -> Product | None:
    if not products:
        return None

    prompt = f"""
            You are an AI shopping assistant.

            Choose the single best product for the user.

            User request:
            {request}

            Structured requirements:
            {requirements}

            Candidate products:
            {json.dumps(products, indent=2)}

            Rules:
            - You MUST choose one product from the candidate products.
            - NEVER invent a product.
            - Use the product's id exactly as provided.
            - Consider the user's request, requirements, description, features and tags.
            - Prefer the product that best matches the user's stated needs, not simply the cheapest product.
            - Return a concise explanation for the recommendation.
            """

    structured_llm = llm.with_structured_output(ProductRecommendation)

    result = structured_llm.invoke(prompt)

    for product in products:
        if product["id"] == result.product_id:
            return {
                **product,
                "recommendation_reason": result.reason,
            }

    return None

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