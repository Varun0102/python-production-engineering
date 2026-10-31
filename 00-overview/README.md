# Overview

## The story

It is Friday night. It is raining, there is an IPL match, and nobody wants to cook. Orders spike, and so do complaints.

- "My card was charged twice for my biryani."
- "My delivery is 50 minutes late."
- "There is a problem with my restaurant order."

Each complaint must reach the right team: Payments, Delivery Ops, Restaurant Support or Refunds. Today a human reads every complaint and decides where it goes. On a Friday night, that does not scale.

So we automate the first step. We build a Complaint Triage Service that reads a complaint and decides:

    category: payments
    priority: 4
    team:     payments

If the service is not confident, or the answer is invalid, the complaint goes to Human Review.

## Concept: what does triage mean?

Triage means sorting. We are not solving the complaint, we are only deciding where it goes and how urgent it is. The teams still do the actual work.

## The four gates

A developer builds this with an AI assistant in 30 minutes and says "It works on my laptop. Let's ship it." Four people say no.

| Gate | Who says no | Their question |
|---|---|---|
| CONTRACT | Head of Support Ops | What exactly can this service return? |
| ASYNC | Support Team Lead | Thousands of complaints, and we are waiting on another system? |
| SERVICE | Security Head | Where are your secrets? Why is customer data in the logs? |
| SHIP | Platform Engineer | How am I going to run this? |

## What you will learn

- HTTP and APIs: how two systems talk
- FastAPI and Uvicorn: turning Python code into a service
- Pydantic: the contract, so bad data cannot get in
- Async: not freezing while we wait for the AI
- Configuration and environment variables
- Secrets: nothing sensitive in code or images
- Structured logging: JSON logs without personal data
- Health checks: running is not the same as healthy
- Git, Docker, Amazon ECR and Amazon EKS: the deployment flow

## Prerequisites

- An AWS account you can use for the lab
- A GitHub account
- Basic Git, Docker and kubectl commands. This is not a Docker or Kubernetes course, we use them as tools.
- Basic Python helps, but every line of code is explained in class.

## Setup checklist (before the class)

- [ ] AWS account ready, region ap-south-1 (Mumbai)
- [ ] AWS CLI installed and configured on your laptop
- [ ] An SSH client: PuTTY on Windows, or the ssh command on Mac and Linux
- [ ] GitHub account
- [ ] A browser with https://app.diagrams.net to open the class diagrams

You do not need Python, Docker or Kubernetes on your laptop. All the work happens on an EC2 workstation in AWS.

## Why this matters for your career

Before this course: "I know Python."

After this course: "I can take a Python API to production. Typed contract with Pydantic, async calls with timeouts, configuration and secrets outside the code, structured JSON logs, health checks, Docker, Amazon ECR and Amazon EKS."

That second sentence is what interviewers for Backend, DevOps, Platform and MLOps roles want to hear.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
