"""FastAPI application for the policy service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from policy.manager import (
    Policy,
    PolicyStatus,
    create_policy,
    activate_policy,
    cancel_policy,
)

app = FastAPI(title="Policy Service", version="0.1.0")

# In-memory store for the demo
_store: dict[str, Policy] = {}


class CreatePolicyRequest(BaseModel):
    holder_name: str = Field(..., min_length=1)
    coverage_amount: float = Field(..., gt=0)


class PolicyResponse(BaseModel):
    policy_id: str
    holder_name: str
    coverage_amount: float
    status: PolicyStatus


class CancelRequest(BaseModel):
    reason: str = ""


def _to_response(p: Policy) -> PolicyResponse:
    return PolicyResponse(
        policy_id=p.policy_id,
        holder_name=p.holder_name,
        coverage_amount=p.coverage_amount,
        status=p.status,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/policies", response_model=PolicyResponse, status_code=201)
def create(req: CreatePolicyRequest) -> PolicyResponse:
    try:
        policy = create_policy(req.holder_name, req.coverage_amount)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _store[policy.policy_id] = policy
    return _to_response(policy)


@app.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: str) -> PolicyResponse:
    policy = _store.get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return _to_response(policy)


@app.post("/policies/{policy_id}/activate", response_model=PolicyResponse)
def activate(policy_id: str) -> PolicyResponse:
    policy = _store.get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    try:
        activate_policy(policy)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_response(policy)


@app.post("/policies/{policy_id}/cancel", response_model=PolicyResponse)
def cancel(policy_id: str, req: CancelRequest) -> PolicyResponse:
    policy = _store.get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    try:
        cancel_policy(policy, req.reason)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_response(policy)
