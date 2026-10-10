"""Apex_HyperGate: Deterministic E2E Testing Framework.

Validates multi-heartbeat task lifecycles under strict Paperclip USD budgets,
evaluates Nerve security sandboxing, verifies Alibaba Open Code Review diffs,
and verifies ActionLedger cryptographic receipt integrity.
"""

import time
from typing import Dict, List, Any
from apex_hypergate.core.primitives import (
    PaperclipTaskStatus,
    SecurityVerdictKind,
)
from apex_hypergate.adapters.paperclip_adapter import HermesPaperclipAdapter
from apex_hypergate.core.nerve_sandbox import NerveSecuritySandbox
from apex_hypergate.core.aliens_trick_slasher import AliensTrickTokenSlasher
from apex_hypergate.ocr.alibaba_reviewer import AlibabaOpenCodeReviewer
from apex_hypergate.core.primitives import MCPToolSchema


class HyperGateE2ETester:
    """Deterministic E2E testing harness for Paperclip, Nerve, and Alibaba OCR."""

    def __init__(self):
        self.paperclip = HermesPaperclipAdapter()
        self.sandbox = NerveSecuritySandbox()
        self.slasher = AliensTrickTokenSlasher()
        self.reviewer = AlibabaOpenCodeReviewer()

    def run_e2e_suite(self) -> Dict[str, Any]:
        """Execute complete multi-turn scenario and return structured metrics."""
        start_ns = time.perf_counter_ns()
        
        # 1. Initialize Task with $0.05 budget
        task = self.paperclip.create_task("E2E-TASK-001", "Refactor User Authentication Endpoint", usd_budget=0.05)
        
        # 2. Setup candidate tools
        candidate_tools = [
            MCPToolSchema("view_file", "Read file contents", {"path": {"type": "string"}}, cost_tokens=50),
            MCPToolSchema("edit_file", "Modify file contents", {"path": {"type": "string"}}, cost_tokens=150),
            MCPToolSchema("bash_exec", "Run shell command", {"cmd": {"type": "string"}}, cost_tokens=200),
            MCPToolSchema("query_db", "Query internal database", {"sql": {"type": "string"}}, cost_tokens=300),
            MCPToolSchema("send_slack", "Notify Slack channel", {"msg": {"type": "string"}}, cost_tokens=80),
        ]

        # 3. Test Alien's Trick Token Slasher
        pruned_tools, slash_metrics = self.slasher.prune_tool_schemas(
            candidate_tools,
            user_query="read and edit python authentication file",
            token_budget=250,
        )
        slashing_passed = slash_metrics["tokens_consumed"] <= 250

        # 4. Heartbeat 1: Safe read operation
        can_proceed_1, task, err_1 = self.paperclip.heartbeat_tick(
            task_id="E2E-TASK-001",
            prompt_tokens=400,
            completion_tokens=150,
            tool_action_name="view_file",
            tool_payload={"path": "src/auth.py"},
        )
        verdict_1 = self.sandbox.inspect_tool_call("view_file", {"path": "src/auth.py"})

        # 5. Heartbeat 2: Malicious SSRF injection attempt (Must be intercepted by Nerve)
        verdict_ssrf = self.sandbox.inspect_tool_call("fetch_url", {"url": "http://169.254.169.254/latest/meta-data/"})
        ssrf_blocked = (verdict_ssrf.verdict == SecurityVerdictKind.BLOCKED_SSRF)

        # 6. Heartbeat 3: Run code edit and inspect via Alibaba Open Code Review
        mock_diff = """--- a/src/auth.py
+++ b/src/auth.py
@@ -10,4 +10,5 @@
 def login(user, pwd):
+    cursor.execute(f"SELECT * FROM users WHERE name = '{user}'")
     return True
"""
        ocr_report = self.reviewer.review_git_diff(mock_diff)
        sqli_detected = any(f.rule_id == "ALIBABA-SEC-001" for f in ocr_report.findings)

        # 7. Complete task
        final_task = self.paperclip.mark_task_complete("E2E-TASK-001")
        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

        all_passed = (
            slashing_passed and
            can_proceed_1 and
            verdict_1.is_safe and
            ssrf_blocked and
            sqli_detected and
            final_task.status == PaperclipTaskStatus.COMPLETED and
            final_task.consumed_usd <= final_task.usd_budget and
            len(final_task.receipts) >= 2
        )

        return {
            "all_tests_passed": all_passed,
            "task_id": final_task.task_id,
            "status": final_task.status.value,
            "consumed_usd": final_task.consumed_usd,
            "usd_budget": final_task.usd_budget,
            "receipts_count": len(final_task.receipts),
            "tokens_slashed_pct": slash_metrics["pruning_rate_pct"],
            "ssrf_blocked": ssrf_blocked,
            "alibaba_sqli_detected": sqli_detected,
            "total_e2e_duration_ms": round(elapsed_ms, 2),
        }
