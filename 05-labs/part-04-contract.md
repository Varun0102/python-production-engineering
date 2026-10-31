# Part 04: Build the Service and Its Contract

Gate 1: CONTRACT. The Head of Support Ops asked: "What exactly can this service return?"

In this part we turn our Python logic into an API with FastAPI, and we give it a contract with Pydantic. By the end you will see FastAPI reject bad data with a 422, before our code even runs.

Run everything in this part on the EC2 workstation.

## Step 1: Install Python 3.11 and create a virtual environment

```bash
sudo dnf install -y python3.11 python3.11-pip
mkdir -p ~/triage/triage-service/app && cd ~/triage/triage-service
python3.11 -m venv .venv
source .venv/bin/activate
python --version
```

Expected: Python 3.11.x

Concept: a virtual environment is a private box of packages for this project. It never clashes with anything else on the machine. Our Docker image will use Python 3.11 too, so what works here works in the container.

## Step 2: Pin the dependencies

```bash
cat > requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
EOF
pip install -r requirements.txt
```

Question: why pin exact versions instead of just writing fastapi?

Because without a pin, the build you run next month may pull a different version than the one you tested today. Pinned versions mean the same code behaves the same way on every machine.

## Step 3: Write the contract

```bash
touch app/__init__.py

cat > app/models.py <<'EOF'
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
EOF
```

Concept: read the contract line by line.

| Rule | What it stops |
|---|---|
| Team is an Enum | "payment team" is rejected. Only the five agreed team names pass |
| priority: int, ge=1, le=4 | "High" and "Urgent" are rejected. Only 1, 2, 3 or 4 pass |
| extra="forbid" | A surprise field like customer_mood is rejected |
| min_length=5 | An empty or one word complaint is rejected |

## Step 4: Write the triage logic

```bash
cat > app/triage.py <<'EOF'
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
EOF
```

Concept: when the rules cannot decide, the complaint goes to human_review. The service never guesses.

## Step 5: Turn it into an API

```bash
cat > app/main.py <<'EOF'
"""Complaint Triage Service, Part 04: the contract."""
from fastapi import FastAPI

from app.models import ComplaintIn, TriageResult
from app.triage import rule_based_triage

app = FastAPI(title="Complaint Triage Service", version="1.0.0")


@app.post("/triage", response_model=TriageResult)
def triage(body: ComplaintIn) -> TriageResult:
    return rule_based_triage(body.complaint)
EOF
```

Concept: three lines do all the work.

- @app.post("/triage") is the endpoint: POST method, /triage address
- body: ComplaintIn tells FastAPI to check every request against the contract before our function runs
- response_model=TriageResult checks what we send back

## Step 6: Run it with Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
sleep 2
cat uvicorn.log
```

Expected: Uvicorn running on http://0.0.0.0:8000

Concept: FastAPI defined the API. Uvicorn is the server that listens on port 8000 and hands each request to FastAPI.

## Step 7: Call it

A good complaint:

```bash
curl -s -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"complaint": "I was charged twice for my biryani"}'
echo
```

Expected:

```
{"category":"payments","priority":4,"team":"payments"}
```

Try one more:

```bash
curl -s -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"complaint": "My food arrived cold"}'
echo
```

## Step 8: Break the contract on purpose

Question: what should happen if the Zomato app sends something we did not agree on?

Too short:

```bash
curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" -d '{"complaint": "hi"}'
```

A field nobody agreed on:

```bash
curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" -d '{"complaint": "Order is late", "customer_mood": "angry"}'
```

Nothing at all:

```bash
curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" -d '{}'
```

Every one returns HTTP 422, with a message that says exactly what was wrong.

Concept: our triage function never ran for these requests. Pydantic stopped them at the door. This is Check 1 from the Pydantic page: the request.

## Step 9: Check 2, the AI answer

In Part 05 an AI model will produce the triage result. Let us see what our contract does with the bad answer from our story.

```bash
python - <<'EOF'
from app.models import TriageResult

bad_ai_answer = {"category": "payment", "priority": "High", "team": "payment team"}
try:
    TriageResult.model_validate(bad_ai_answer)
except Exception as error:
    print(error)
EOF
```

Expected: 3 validation errors for TriageResult, one for each wrong field.

Concept: this is Check 2. In Part 05, when the AI answer fails this check, the complaint goes to Human Review instead of the wrong queue.

## Step 10: The free documentation (optional)

FastAPI generates interactive docs at /docs. To open them in your browser:

1. In the console, open the security group triage-workstation-sg, Edit inbound rules
2. Add: Custom TCP, port 8000, Source: My IP. Save
3. Open http://PUBLIC_IP:8000/docs

Concept: nobody wrote this page. FastAPI built it from our contract. The consuming team can read exactly what we accept and what we return.

## Step 11: Stop the server

```bash
kill %1
```

## What you built

- An API with one endpoint, POST /triage
- A contract that rejects bad requests with 422 (Check 1)
- A contract that catches a bad AI answer (Check 2)

The CONTRACT gate is passed. Next: Part 05, the ASYNC gate.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
