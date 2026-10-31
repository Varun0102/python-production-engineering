# Interview Questions

Answer these from what you built in the lab, not from memorized definitions. More questions are added as each lab part is completed.

## The service

1. What is the difference between a script and a service?
2. What happens when the Zomato app calls an API? Walk through the request and the response.
3. What is the difference between GET and POST? Why is /triage a POST?
4. What is the difference between 4xx and 5xx status codes? When does an API return 422?
5. What is the difference between FastAPI and Uvicorn?

## Contract

6. What problem does Pydantic solve?
7. Pydantic checks data in two places in our service. Where, and what happens when each check fails?
8. Why should a model's output be treated as untrusted input?

## Async

9. Why does async def alone not make code asynchronous?
10. requests versus httpx.AsyncClient: what is the difference?
11. Why does every external call need a timeout?
12. Why can retries be dangerous?

## Service

13. Configuration versus secrets: what is the difference?
14. Why should a secret never be inside a Docker image?
15. What is structured logging, and what must never appear in logs?
16. Why do we need /healthz? Running versus healthy?
17. Liveness probe versus readiness probe?

## Ship

18. Walk me through your deployment flow, from code to a running service.
19. Why attach an IAM role to EC2 instead of storing access keys on it?
20. A pod starts and immediately crashes. How do you debug it?

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
