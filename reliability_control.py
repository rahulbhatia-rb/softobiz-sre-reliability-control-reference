#!/usr/bin/env python3
"""A deterministic release gate for AWS services operated with Terraform.

The intent is deliberately modest: turn the evidence an SRE needs during a
change into an explicit, auditable go/no-go decision.  The gate never applies
Terraform; it tells the deployment system when a human review is required.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    severity: str
    control: str
    message: str


def evaluate(change: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    infra = change.get("terraform", {})
    service = change.get("service", {})
    observability = change.get("observability", {})
    incident = change.get("incident", {})

    if not infra.get("plan_reviewed"):
        findings.append(Finding("block", "terraform-plan", "Terraform plan has not been reviewed."))
    if infra.get("destructive_changes", 0) > 0 and not infra.get("approved_change_ticket"):
        findings.append(Finding("block", "terraform-destroy", "Destructive Terraform change lacks an approved change ticket."))
    if not service.get("multi_az"):
        findings.append(Finding("block", "availability", "Production service is not configured for multi-AZ resilience."))
    if not service.get("rollback_runbook"):
        findings.append(Finding("block", "rollback", "No tested rollback runbook is attached to this deployment."))
    if observability.get("slo_error_budget_remaining", 0) < 15:
        findings.append(Finding("block", "slo-budget", "Error-budget headroom is below the 15% deployment threshold."))
    if not observability.get("alerts_tested"):
        findings.append(Finding("warn", "alerts", "Alert path has not been tested for this release."))
    if incident.get("open_sev1_or_sev2"):
        findings.append(Finding("block", "incident-freeze", "A high-severity incident is open; freeze non-essential changes."))
    if not incident.get("on_call_owner"):
        findings.append(Finding("warn", "ownership", "No on-call owner was assigned to the change window."))
    return findings


def decision(findings: list[Finding]) -> str:
    return "BLOCK" if any(f.severity == "block" for f in findings) else "ALLOW"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate SRE release evidence")
    parser.add_argument("evidence", type=Path, help="JSON release-evidence file")
    args = parser.parse_args()
    findings = evaluate(json.loads(args.evidence.read_text()))
    print(json.dumps({"decision": decision(findings), "findings": [asdict(f) for f in findings]}, indent=2))
    return 1 if decision(findings) == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
