# Razorpay Agentic Commerce

A two-sided agentic commerce system built for the Razorpay AI Buildathon 2026 (Track 01: AI Growth & Agentic Commerce). One side lets an AI agent act as a buyer — understanding a natural-language request, recommending a product, and completing a Razorpay Test Mode purchase after human approval. The other side lets an AI agent act as a merchant assistant — analyzing a product catalog, finding a cross-sell opportunity, and proposing a growth campaign, again gated by human approval.

The system is not a chatbot bolted onto a store. It's an attempt to answer a narrower, harder question: if AI agents are going to browse catalogs and initiate purchases, and if AI is going to help merchants grow revenue, what does the trust boundary between "AI decides" and "system executes" actually look like?

## Why This Exists

Traditional ecommerce assumes a human is sitting in front of a browser, clicking "buy." That assumption is starting to break. AI agents increasingly need structured, trustworthy ways to discover and purchase products on a buyer's behalf. At the same time, merchants need a way to become legible and relevant to those AI buyers — and ideally, to have AI help them grow revenue rather than just process orders.

Both directions raise the same problem: an LLM is good at understanding intent and proposing options, and bad at being trusted with anything that costs money or is hard to undo. This project is built around that constraint rather than around it.

## What I Built

**AI Buyer** — takes a plain-English request ("I need a laptop for software development under ₹80,000"), extracts structured requirements with an LLM, filters the catalog deterministically, asks the LLM to recommend one product from the filtered candidates with a reason, pauses for human approval, runs a deterministic policy check, creates a real Razorpay Test Mode order, and logs the whole thing.

**AI Merchant** — takes the merchant's catalog, asks an LLM to find the strongest cross-sell opportunity in it (not hardcoded — it's asked to reason over all 46 products), asks the LLM to turn that opportunity into a campaign proposal, pauses for merchant approval, deterministically creates the campaign record, and logs it.

Same shape on both sides: **reason → propose → approve → enforce → execute → audit.**

## Architecture

```
                         FastAPI
                            │
              ┌─────────────┴─────────────┐
              │                           │
         Buyer Agent                Merchant Agent
              │                           │
              └─────────────┬─────────────┘
                            │
                    LLM reasoning layer
                            │
                   Human approval
                            │
                 Deterministic tools
                            │
                   Razorpay / Audit
```

Both agents are LangGraph state machines. Both interrupt for approval at the point where a decision stops being reversible. Both hand off to plain, boring, deterministic Python once approval is granted.

## AI Buyer

Graph:

```
START
 ↓
understand_request
 ↓
search_catalog
 ↓
recommend_product
 ↓
approval
 ↓
approved?
 ├── yes → policy_check
 └── no  → audit_transaction

policy_check
 ↓
allowed?
 ├── yes → create_payment
 └── no  → audit_transaction

create_payment
 ↓
audit_transaction
 ↓
END
```

1. **Understand request** — Gemini extracts structured requirements (`category`, `price`, `currency`) from free text, via `llm.with_structured_output(RequirementExtraction)`. This replaced an earlier regex/exact-match approach that couldn't handle phrasing variance ("laptop for programming, maximum budget is eighty thousand rupees" vs. "laptop under ₹80,000").
2. **Search catalog** — plain, deterministic filtering against the 46-product catalog. The LLM never sees the whole catalog at this stage; it only ever sees candidates that are already valid.
3. **Recommend product** — Gemini picks exactly one product from the filtered candidates (never invents one) and returns a structured `ProductRecommendation` with a reason. The returned product ID is checked against the actual candidates before being trusted:

   ```python
   for product in products:
       if product["id"] == result.product_id:
           return {**product, "recommendation_reason": result.reason}
   return None
   ```

4. **Human approval** — the graph interrupts and returns the recommendation to the caller for a yes/no.
5. **Policy check** — deterministic: user approval, recommendation existence, price vs. requested max, currency match, availability. The LLM has no vote here.
6. **Razorpay order** — a real Test Mode order is created via the Razorpay Python SDK, credentials loaded from environment variables.
7. **Audit** — every run, approved or not, writes a JSON audit record.

## AI Merchant

Graph:

```
detect_opportunity
        ↓
generate_campaign
        ↓
approval
        ↓
approved?
 ├── yes → create_campaign
 └── no  → audit_campaign
```

1. **Detect opportunity** — Gemini is given the full catalog and asked to find the strongest cross-sell relationship, constrained to categories that actually exist in the catalog. This replaced an earlier hardcoded `running_shoe → socks` rule. In testing it has independently surfaced relationships like `laptop → laptop_stand` and `laptop → monitor`, with reasoning like: laptops are high-value anchor products for developers, and a discounted external monitor completes the workstation setup while meaningfully raising average order value.
2. **Generate campaign** — Gemini turns the opportunity into a structured `MerchantCampaign`: name, source/target category, offer, and rationale. This is a proposal, not an action — Gemini never touches anything that changes state.
3. **Merchant approval** — another LangGraph interrupt, same pattern as the buyer side.
4. **Create campaign** — deterministic. Adds `"status": "created"` to the record. No LLM in this path.
5. **Audit** — campaign, approval, status, and type are logged to JSON.

## Human-in-the-Loop

Both graphs use LangGraph's `interrupt()` to pause execution right before a consequential step, and `MemorySaver` for checkpointing so the paused state can be resumed later on the same thread via `Command(resume=...)`. This is the actual mechanism behind "the human approves consequential actions" — it's not a UI convention, it's baked into the graph: there is no code path from LLM output to payment or campaign creation that doesn't pass through an interrupt first.

## AI vs. Deterministic Boundaries

| Responsibility | AI | Deterministic |
|---|---|---|
| Requirement extraction | ✅ | |
| Catalog filtering | | ✅ |
| Product recommendation | ✅ | |
| Policy validation | | ✅ |
| Payment / order creation | | ✅ |
| Opportunity detection | ✅ | |
| Campaign proposal | ✅ | |
| Campaign creation | | ✅ |
| Audit logging | | ✅ |

The rule of thumb: if it's about *understanding or proposing*, it's the LLM's job. If it's about *money, state changes, or record-keeping*, it's plain code, and the LLM's output is only ever an input to it — never the thing that executes it.

## Tech Stack

- Python, FastAPI, Uvicorn
- LangGraph, LangChain, `langchain-google-genai`
- Google Gemini (`gemini-3.6-flash`, structured output via Pydantic)
- Razorpay Python SDK (Test Mode)
- JSON-based audit logs
- Go (currently just a minimal HTTP health-check server — not part of agent orchestration, which lives entirely in Python/FastAPI)

## Project Structure

```
backend/
├── agent/
│   ├── buyer/
│   │   ├── agent.py
│   │   ├── test_agent.py
│   │   └── utils/
│   │       ├── nodes.py
│   │       ├── state.py
│   │       └── tools.py
│   └── merchant/
│       ├── agent.py
│       ├── test_agent.py
│       └── utils/
│           ├── nodes.py
│           ├── state.py
│           └── tools.py
├── api/
│   └── main.py
├── buyer_audit_log.json
├── merchant_audit_log.json
└── cmd/
    └── api/
        └── main.go
```

## Running Locally

From the project root:

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export GEMINI_API_KEY=your_key_here
export RAZORPAY_KEY_ID=your_test_key_id
export RAZORPAY_KEY_SECRET=your_test_key_secret

uvicorn backend.api.main:app --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Start a buyer flow:

```bash
curl -X POST http://localhost:8000/buyer/start \
  -H "Content-Type: application/json" \
  -d '{"request": "I need a laptop for software development under ₹80,000"}'
```

Approve it (using the `thread_id` returned above):

```bash
curl -X POST http://localhost:8000/buyer/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "THREAD_ID_HERE", "approved": true}'
```

Merchant flow follows the same shape via `/merchant/start` and `/merchant/approve`.

## Example: Buyer Request

Request: *"I need a laptop for software development under ₹80,000"*

Gemini extracts `{category: laptop, price: 80000, currency: INR}`. Deterministic filtering narrows the catalog down to candidates matching that budget and category. Gemini picks one — in one tested run, the **CodeMaster 14** at ₹78,000, with the reasoning: it fits software development under ₹80,000 given its 16GB RAM, Ryzen 7 processor, and 1TB SSD for handling build artifacts and virtual environments. (Other valid runs have selected **DevBook Pro** instead — the point isn't a fixed answer, it's that the answer always comes from the real candidate list.) After approval, the policy check passes, a Razorpay Test Mode order is created, and the transaction is audited.

## Example: Merchant Opportunity

Gemini analyzes the catalog and surfaces `laptop → monitor` as the strongest cross-sell opportunity, reasoning that laptops are high-value anchor purchases for developers and professionals, and a discounted monitor completes their workstation setup while increasing average order value. It then generates a campaign:

- **Name:** Complete Workstation Bundle
- **Offer:** 15% off any CodeView or UltraWide monitor when added alongside any developer laptop
- **Reason:** completes the buyer's setup, raises average order value

After merchant approval, the campaign is created deterministically and audited.

## Current Limitations

This is a working prototype, and it's honest about the gap between that and production:

- The catalog is defined in Python, not stored in a persistent database.
- LangGraph uses `MemorySaver` for checkpointing — state isn't backed by a durable, production-grade store yet.
- Audit logs are JSON files, not a database.
- The system models a single merchant catalog, not a multi-merchant marketplace.
- Razorpay integration creates Test Mode orders — this is not a full production payment lifecycle.
- There's no payment idempotency yet, so calling `/buyer/approve` twice could create duplicate orders.
- No frontend, no production deployment, no MCP server.

## Future Roadmap

- **PostgreSQL** for durable state (`merchants`, `products`, `orders`, `campaigns`, `audit_events`), with a small repository/data-access layer sitting between the app and the database.
- **MCP server** exposing controlled tools (`search_products`, `get_product`, `get_catalog`, `get_product_performance`, `get_related_products`) so the LLM interacts with commerce data through a defined tool boundary rather than any direct database access:

  ```
                           FastAPI
                              │
                ┌─────────────┴─────────────┐
                │                           │
           Buyer Agent                Merchant Agent
                │                           │
                └─────────────┬─────────────┘
                              │
                         MCP Server
                              │
                         Data Layer
                              │
                         PostgreSQL
                              │
                ┌─────────────┼──────────────┐
                │             │              │
             Catalog        Orders        Campaigns
                                               │
                                             Audit
  ```

  Razorpay stays behind the same deterministic boundary it's behind today.

- **Multi-merchant catalog** — each merchant owning its own products and campaigns, with buyer search operating across merchants.
- **Order lifecycle** as an explicit state machine: `PENDING_APPROVAL → APPROVED → POLICY_CHECKED → ORDER_CREATED → PAYMENT_PENDING → PAID`.
- **Idempotency** — an idempotency key on approval requests so a duplicate `/buyer/approve` call returns the existing order instead of creating a new one.
- **Structured audit storage** in PostgreSQL instead of JSON files.
- **A minimal frontend** that walks through the full flow end-to-end: request → recommendation → reason → approval → policy result → Razorpay order, and opportunity → campaign → approval → audit on the merchant side.

All of the above is planned, none of it exists yet — the current system stops at Test Mode orders, JSON audit logs, and an in-memory graph checkpoint.

## Design Principles

- AI proposes, deterministic code executes.
- Anything consequential (money, campaign creation) requires human approval first.
- LLM outputs are always structured (Pydantic), never free-text parsed for logic.
- Every run — approved, rejected, or policy-blocked — gets audited.
- Tool boundaries stay narrow: the LLM only ever sees data it's allowed to reason over, never a path to directly change state.
- Financial execution stays deterministic, full stop.

## Build / Technical Challenges

The interesting problems here weren't "how do I call an LLM" — they were around the seams:

- Getting Gemini to reliably return structured output that maps cleanly onto internal types, rather than free text you have to parse and hope.
- Bridging natural-language phrasing against rigid catalog naming (e.g., the LLM saying "running shoes" when the catalog stores `running_shoe`) — solved for now with a small category-alias map, which is an obvious spot for more coverage later.
- Managing human-in-the-loop state correctly across an interrupted graph — making sure a paused workflow resumes from the same point rather than silently restarting.
- Keeping the LLM's role bounded to reasoning and proposals even when it would be technically easier to let it "just decide" — the policy check and campaign creation paths were deliberately written to never trust an LLM-returned boolean.
- Wiring up a real Razorpay Test Mode order rather than mocking payment entirely, so the flow is genuinely end-to-end.
- Replacing a hardcoded cross-sell rule with actual LLM reasoning over the catalog, and verifying it wasn't just memorizing the one example — testing confirmed it surfaces different valid opportunities (`laptop → laptop_stand`, `laptop → monitor`) depending on how it reasons about the catalog.

## Future Interview Discussion

Topics this project touches, in case it comes up:

- LangGraph for stateful, interruptible agent orchestration
- Structured LLM outputs as a trust boundary, not just a formatting convenience
- Human-in-the-loop design for irreversible actions
- Deterministic policy enforcement sitting between AI output and execution
- Payment workflow integration (Razorpay Test Mode)
- Idempotency as a reliability concern for anything that touches money
- MCP as a way to bound what tools an LLM can call, rather than giving it raw data access
- PostgreSQL as the eventual home for durable business state, once the prototype outgrows in-memory checkpoints
