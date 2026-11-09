# Softobiz SRE Reliability Control Reference

A runnable, policy-as-code proof of concept for the Site Reliability Engineer role (GG-1531). It models the release controls that keep an AWS service safe while Terraform, observability, and incident response workflows move quickly.

## What this demonstrates

The release gate turns deployment evidence into a deterministic **ALLOW** or **BLOCK** decision. It checks:

- Terraform plan review and an approved change ticket before destructive changes.
- Multi-AZ service resilience and an attached rollback runbook.
- SLO error-budget headroom (at least 15%) before a production change.
- Tested alert paths, named on-call ownership, and an incident freeze for active Sev1/Sev2 events.

This mirrors a practical SRE loop: Terraform creates reproducible infrastructure, CloudWatch/Prometheus/Grafana provide evidence, CI invokes the gate, and an on-call engineer retains final control of production changes.

## Run it

```bash
python3 reliability_control.py examples.json
python3 -m unittest discover -s tests -v
```

The included evidence file is healthy and returns `ALLOW`. A failed check returns `BLOCK` and a non-zero exit code, making it suitable for a GitHub Actions, Jenkins, or GitLab CI stage.

## Deployment flow

```text
Terraform plan → policy/reliability gate → human approval → deploy
       ↑                  ↑                    ↓
 AWS topology       SLO + alerts        rollback runbook
       ↑                  ↑                    ↓
CloudWatch / Prometheus ← incident response → post-incident actions
```

## Why it matters

Reliability is not a dashboard after deployment. This POC demonstrates how to make incident posture, SLO health, infrastructure drift risk, and rollback readiness first-class inputs to delivery. The policy is intentionally transparent and testable; it is easy to extend with OPA, Terraform plan JSON, AWS Config/Security Hub signals, or a service catalog.

## Rahul H Bhatia

AWS, Kubernetes, Terraform, CI/CD, observability, production operations, and GenAI/RAG delivery.

- LinkedIn: https://www.linkedin.com/in/rahul-h-bhatia/
- Portfolio: https://rahulhbhatia.vercel.app
