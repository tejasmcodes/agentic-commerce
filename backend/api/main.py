from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

from langgraph.types import Command
from backend.agent.buyer.agent import buyer_agent
from backend.agent.merchant.agent import merchant_agent

app = FastAPI(title="Razorpay AI Commerce")


class BuyerStartRequest(BaseModel):
    request: str


class BuyerApprovalRequest(BaseModel):
    thread_id: str
    approved: bool


class MerchantApprovalRequest(BaseModel):
    thread_id: str
    approved: bool

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/buyer/start")
def buyer_start(payload: BuyerStartRequest):
    thread_id = str(uuid4())

    initial_state = {
        "request": payload.request,
        "requirements": {},
        "products": [],
        "recommendation": None,
        "approved": False,
        "policy_result": {},
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = buyer_agent.invoke(initial_state, config)

    interrupt = result["__interrupt__"][0]

    return {
        "thread_id": thread_id,
        "status": "awaiting_approval",
        "approval": interrupt.value,
    }


@app.post("/buyer/approve")
def buyer_approve(payload: BuyerApprovalRequest):
    config = {
        "configurable": {
            "thread_id": payload.thread_id
        }
    }

    result = buyer_agent.invoke(
        Command(resume=payload.approved),
        config,
    )

    return {
        "status": "completed",
        "result": result,
    }


@app.post("/merchant/start")
def merchant_start():
    thread_id = str(uuid4())

    initial_state = {
        "opportunity": None,
        "campaign": None,
        "approved": False,
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = merchant_agent.invoke(initial_state, config)

    interrupt = result["__interrupt__"][0]

    return {
        "thread_id": thread_id,
        "status": "awaiting_approval",
        "approval": interrupt.value,
    }


@app.post("/merchant/approve")
def merchant_approve(payload: MerchantApprovalRequest):
    config = {
        "configurable": {
            "thread_id": payload.thread_id
        }
    }

    result = merchant_agent.invoke(
        Command(resume=payload.approved),
        config,
    )

    return {
        "status": "completed",
        "result": result,
    }