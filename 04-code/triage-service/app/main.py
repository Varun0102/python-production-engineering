"""Complaint Triage Service, Part 04: the contract."""
from fastapi import FastAPI

from app.models import ComplaintIn, TriageResult
from app.triage import rule_based_triage

app = FastAPI(title="Complaint Triage Service", version="1.0.0")


@app.post("/triage", response_model=TriageResult)
def triage(body: ComplaintIn) -> TriageResult:
    return rule_based_triage(body.complaint)
