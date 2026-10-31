# The Lab: Complaint Triage Service, from Zero to Amazon EKS

This is one lab, built step by step. Every part builds on the previous one, so follow them in order.

| Part | What you do | Gate |
|---|---|---|
| 01 | Create the VPC and subnets (AWS CLI) | Setup |
| 02 | Launch the EC2 workstation with an IAM role (AWS console) | Setup |
| 03 | Install Docker, kubectl, eksctl and create the EKS cluster | Setup |
| 04 | Build the service: FastAPI and the Pydantic contract | CONTRACT |
| 05 | Call the AI stub with async httpx and a timeout | ASYNC |
| 06 | Configuration, secrets, JSON logs, /healthz | SERVICE |
| 07 | Git, Docker image, push to Amazon ECR | SHIP |
| 08 | Deploy to Amazon EKS | SHIP |
| 09 | Break it and diagnose it | SHIP |
| 10 | Clean up everything | Cleanup |

Parts are added as the class progresses.

Concept: we keep ONE application all day. Every part adds one production capability to the same service.

## Names used in this lab

| Resource | Name |
|---|---|
| Region | ap-south-1 (Mumbai) |
| VPC | triage-vpc (10.0.0.0/16) |
| Subnets | triage-public-a (10.0.1.0/24), triage-public-b (10.0.2.0/24) |
| Key pair | triage-key |
| IAM role | triage-workstation-role |
| Security group | triage-workstation-sg |
| EC2 instance | triage-workstation |
| EKS cluster | triage-cluster |
| EKS node group | triage-nodes |

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
