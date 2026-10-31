# The Lab: Complaint Triage Service, from Zero to Amazon EKS

This is one lab, built step by step. Every part builds on the previous one, so follow them in order.

| Part | What you do | Gate |
|---|---|---|
| 01 | Build your AWS workstation: VPC, EC2, IAM role | Setup |
| 02 | Install the tools and start the EKS cluster | Setup |
| 03 | Build the service: FastAPI, Pydantic contract | CONTRACT |
| 04 | Call the AI stub with async httpx and a timeout | ASYNC |
| 05 | Configuration, secrets, JSON logs, /healthz | SERVICE |
| 06 | Git, Docker image, push to Amazon ECR | SHIP |
| 07 | Deploy to Amazon EKS | SHIP |
| 08 | Break it and diagnose it | SHIP |
| 09 | Clean up everything | Cleanup |

Parts are added as the class progresses.

Concept: we keep ONE application all day. Every part adds one production capability to the same service.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
