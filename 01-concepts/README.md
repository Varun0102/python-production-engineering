# Concepts

Each page here matches a page in 03-diagrams/python-production-engineering.drawio.

| Page | Topic | The one idea to remember |
|---|---|---|
| 01 | The Big Story | Writing the Python code is only the beginning |
| 02 | API and HTTP | An API is the boundary between systems. HTTP is how they talk across it |
| 03 | FastAPI and Uvicorn | FastAPI defines the API. Uvicorn is the server that runs it |
| 04 | Pydantic, the Contract | Never trust data that arrives. Check the request, and check the AI answer |
| 05 | Async | Async is about waiting efficiently. The AI does not get faster, we stop sitting idle |
| 06 | Configuration | Build once, configure at runtime |
| 07 | Secrets | Secrets arrive at runtime. Never in code, never in the image |
| 08 | Structured Logging | Enough information to diagnose, without exposing sensitive data |
| 09 | Health Checks | Running is not healthy |
| 10 | What We Are Going to Build | The full architecture on Amazon EKS |

## Concept: Pydantic checks twice

1. At the door: the request from the Zomato app. Bad request returns 422.
2. Before we trust the AI: the AI answer. Invalid answer goes to Human Review.

## Concept: async alone is not magic

Writing async def and then calling requests.post still blocks. We use httpx.AsyncClient and await the call.

## Concept: configuration is not automatically a secret

LOG_LEVEL=INFO is configuration. AI_API_KEY is a secret. Both stay outside the code. On EKS, configuration goes in a ConfigMap and secrets go in a Kubernetes Secret.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
