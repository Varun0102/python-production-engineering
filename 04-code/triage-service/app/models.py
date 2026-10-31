"""The contract: what our service accepts and what it is allowed to return."""
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    payments = "payments"
    delivery = "delivery"
    restaurant = "restaurant"
    refund = "refund"
    unknown = "unknown"


class Team(str, Enum):
    payments = "payments"
    delivery_ops = "delivery_ops"
    restaurant_support = "restaurant_support"
    refunds = "refunds"
    human_review = "human_review"


class ComplaintIn(BaseModel):
    """What the Zomato app sends us."""
    model_config = ConfigDict(extra="forbid")

    complaint: str = Field(min_length=5, max_length=2000)
    order_id: str | None = None


class TriageResult(BaseModel):
    """What we promise to send back."""
    model_config = ConfigDict(extra="forbid")

    category: Category
    priority: int = Field(ge=1, le=4)
    team: Team
