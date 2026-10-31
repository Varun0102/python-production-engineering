"""Simple keyword rules. In Part 05 an AI model takes over this decision."""
from app.models import Category, Team, TriageResult


def rule_based_triage(complaint: str) -> TriageResult:
    text = complaint.lower()

    if "charged" in text or "payment" in text or "upi" in text:
        return TriageResult(category=Category.payments, priority=4, team=Team.payments)
    if "refund" in text:
        return TriageResult(category=Category.refund, priority=3, team=Team.refunds)
    if "late" in text or "delivery" in text or "rider" in text:
        return TriageResult(category=Category.delivery, priority=3, team=Team.delivery_ops)
    if "cold" in text or "missing" in text or "restaurant" in text:
        return TriageResult(category=Category.restaurant, priority=2, team=Team.restaurant_support)

    return TriageResult(category=Category.unknown, priority=2, team=Team.human_review)
