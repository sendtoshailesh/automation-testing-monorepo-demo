"""FastAPI application for the pricing service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from pricing.calculator import calculate_premium, apply_discount

app = FastAPI(title="Pricing Service", version="0.1.0")


class PremiumRequest(BaseModel):
    age: int = Field(..., ge=0, description="Age of the insured person")
    risk_level: str = Field(..., description="Risk level: low | medium | high")
    discount_pct: float = Field(0.0, ge=0, le=100, description="Discount percentage")


class PremiumResponse(BaseModel):
    premium: float
    discounted_premium: float
    risk_level: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/premium", response_model=PremiumResponse)
def get_premium(req: PremiumRequest) -> PremiumResponse:
    try:
        premium = calculate_premium(req.age, req.risk_level)
        discounted = apply_discount(premium, req.discount_pct)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PremiumResponse(
        premium=premium,
        discounted_premium=discounted,
        risk_level=req.risk_level,
    )
