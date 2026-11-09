import unittest

from reliability_control import decision, evaluate


class ReliabilityControlTests(unittest.TestCase):
    def test_allows_healthy_change(self):
        findings = evaluate({
            "terraform": {"plan_reviewed": True, "destructive_changes": 0},
            "service": {"multi_az": True, "rollback_runbook": "rb"},
            "observability": {"slo_error_budget_remaining": 50, "alerts_tested": True},
            "incident": {"open_sev1_or_sev2": False, "on_call_owner": "sre"},
        })
        self.assertEqual(decision(findings), "ALLOW")

    def test_blocks_unsafe_change(self):
        findings = evaluate({
            "terraform": {"plan_reviewed": False, "destructive_changes": 1},
            "service": {"multi_az": False, "rollback_runbook": ""},
            "observability": {"slo_error_budget_remaining": 1, "alerts_tested": False},
            "incident": {"open_sev1_or_sev2": True, "on_call_owner": ""},
        })
        self.assertEqual(decision(findings), "BLOCK")


if __name__ == "__main__":
    unittest.main()
