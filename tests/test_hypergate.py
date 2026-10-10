"""Unit and Benchmark Test Suite for Apex_HyperGate.

Verifies Alien's Trick token slashing, Nerve security sandboxing, Radix KV-routing,
Hermes Paperclip Company OS budget governance, Alibaba Open Code Review, and E2E testing.
"""

import unittest
import time
from apex_hypergate.core.primitives import (
    MCPToolSchema,
    SecurityVerdictKind,
    PaperclipTaskStatus,
    ReviewSeverity,
)
from apex_hypergate.core.aliens_trick_slasher import AliensTrickTokenSlasher
from apex_hypergate.core.nerve_sandbox import NerveSecuritySandbox
from apex_hypergate.core.radix_router import RadixPrefixKVRouter
from apex_hypergate.core.config_manager import ClientConfigManager
from apex_hypergate.adapters.paperclip_adapter import HermesPaperclipAdapter
from apex_hypergate.ocr.alibaba_reviewer import AlibabaOpenCodeReviewer
from apex_hypergate.eval.e2e_testing import HyperGateE2ETester
from apex_hypergate.orchestrator import ApexHyperGateOrchestrator


class TestApexHyperGate(unittest.TestCase):

    def setUp(self):
        self.orchestrator = ApexHyperGateOrchestrator()

    # --- 1. Alien's Trick WQS Token Slasher ---

    def test_aliens_trick_token_slashing(self):
        slasher = AliensTrickTokenSlasher()
        tools = [
            MCPToolSchema(f"tool_{i}", f"Description for tool {i} with keywords database network query", {}, cost_tokens=80)
            for i in range(20)
        ]
        
        pruned, metrics = slasher.prune_tool_schemas(tools, user_query="database query", token_budget=400)
        self.assertLessEqual(metrics["tokens_consumed"], 400)
        self.assertGreaterEqual(len(pruned), 1)
        self.assertGreater(metrics["pruning_rate_pct"], 60.0)
        self.assertLessEqual(metrics["latency_us"], 5000.0)

    # --- 2. Nerve Security Sandbox & SSRF Firewall ---

    def test_nerve_sandbox_ssrf_blocking(self):
        sandbox = NerveSecuritySandbox()
        
        # Test AWS metadata IP
        v1 = sandbox.inspect_tool_call("fetch", {"url": "http://169.254.169.254/metadata"})
        self.assertEqual(v1.verdict, SecurityVerdictKind.BLOCKED_SSRF)
        self.assertFalse(v1.is_safe)

        # Test Google Cloud metadata
        v2 = sandbox.inspect_tool_call("fetch", {"endpoint": "http://metadata.google.internal/compute"})
        self.assertEqual(v2.verdict, SecurityVerdictKind.BLOCKED_SSRF)

        # Test Private RFC 1918 range
        v3 = sandbox.inspect_tool_call("http_get", {"uri": "http://192.168.1.50:8080"})
        self.assertEqual(v3.verdict, SecurityVerdictKind.BLOCKED_SSRF)

    def test_nerve_sandbox_path_traversal(self):
        sandbox = NerveSecuritySandbox()
        v = sandbox.inspect_tool_call("cat", {"path": "/etc/shadow"})
        self.assertEqual(v.verdict, SecurityVerdictKind.BLOCKED_PATH_TRAVERSAL)
        self.assertFalse(v.is_safe)

        v_ssh = sandbox.inspect_tool_call("view_file", {"TargetFile": "/home/user/.ssh/id_rsa"})
        self.assertEqual(v_ssh.verdict, SecurityVerdictKind.BLOCKED_PATH_TRAVERSAL)

    def test_nerve_sandbox_destructive_commands(self):
        sandbox = NerveSecuritySandbox()
        v = sandbox.inspect_tool_call("bash", {"command": "rm -rf / --no-preserve-root"})
        self.assertEqual(v.verdict, SecurityVerdictKind.BLOCKED_DESTRUCTIVE)

        v_fork = sandbox.inspect_tool_call("sh", {"cmd": ":(){ :|:& };:"})
        self.assertEqual(v_fork.verdict, SecurityVerdictKind.BLOCKED_DESTRUCTIVE)

    # --- 3. Radix-Trie Prefix KV-Cache Router ---

    def test_radix_prefix_kv_router_canonical_ordering(self):
        router = RadixPrefixKVRouter()
        tools_a = [
            MCPToolSchema("zebra", "Zebra tool", {}),
            MCPToolSchema("apple", "Apple tool", {}),
        ]
        tools_b = [
            MCPToolSchema("apple", "Apple tool", {}),
            MCPToolSchema("zebra", "Zebra tool", {}),
        ]

        sorted_a = router.serialize_canonical_prompt_block(tools_a)
        sorted_b = router.serialize_canonical_prompt_block(tools_b)
        # Canonical sort must produce identical strings regardless of input order
        self.assertEqual(sorted_a, sorted_b)

        # Test Radix Trie prefix caching
        hit1 = router.record_and_route_prefix("SESSION-1", sorted_a)
        self.assertFalse(hit1)  # First query is a miss
        hit2 = router.record_and_route_prefix("SESSION-2", sorted_a)
        self.assertTrue(hit2)   # Second identical prefix is a hit!
        self.assertEqual(router.cache_affinity_rate, 50.0)

    # --- 4. Client Config Manager ---

    def test_client_config_manager_injection(self):
        import tempfile
        import os
        manager = ClientConfigManager()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            success = manager.configure_client(tmp_path, port=9000)
            self.assertTrue(success)
            with open(tmp_path, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                self.assertIn("mcpServers", data)
                self.assertIn("apex-hypergate", data["mcpServers"])
                self.assertIn("--port", data["mcpServers"]["apex-hypergate"]["args"])
                self.assertIn("9000", data["mcpServers"]["apex-hypergate"]["args"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # --- 5. Hermes Paperclip Adapter ---

    def test_hermes_paperclip_adapter_budget_governance(self):
        adapter = HermesPaperclipAdapter()
        task = adapter.create_task("TEST-01", "Refactor authentication", usd_budget=0.001)

        # Tick 1: Small cost, should pass
        ok1, t1, err1 = adapter.heartbeat_tick("TEST-01", prompt_tokens=100, completion_tokens=20)
        self.assertTrue(ok1)
        self.assertEqual(t1.status, PaperclipTaskStatus.IN_PROGRESS)

        # Tick 2: Huge token consumption exceeding $0.001 budget
        ok2, t2, err2 = adapter.heartbeat_tick("TEST-01", prompt_tokens=500_000, completion_tokens=100_000)
        self.assertFalse(ok2)
        self.assertEqual(t2.status, PaperclipTaskStatus.BUDGET_EXCEEDED)
        self.assertIn("Budget exceeded", err2)

    def test_hermes_paperclip_action_ledger_receipts(self):
        adapter = HermesPaperclipAdapter()
        adapter.create_task("TEST-02", "Audit database", usd_budget=1.0)
        adapter.heartbeat_tick("TEST-02", 50, 10, "view_file", {"path": "schema.sql"})
        task = adapter.mark_task_complete("TEST-02")
        self.assertEqual(task.status, PaperclipTaskStatus.COMPLETED)
        self.assertGreaterEqual(len(task.receipts), 2)
        for r in task.receipts:
            self.assertEqual(len(r), 64)  # Valid SHA-256

    # --- 6. Alibaba Open Code Review ---

    def test_alibaba_open_code_reviewer_sqli_detection(self):
        reviewer = AlibabaOpenCodeReviewer()
        diff = """--- a/user.py
+++ b/user.py
@@ -10,2 +10,3 @@
 def get_user(uid):
+    cursor.execute(f"SELECT * FROM users WHERE id = '{uid}'")
     return None
"""
        report = reviewer.review_git_diff(diff)
        sqli = [f for f in report.findings if f.rule_id == "ALIBABA-SEC-001"]
        self.assertEqual(len(sqli), 1)
        self.assertEqual(sqli[0].severity, ReviewSeverity.CRITICAL)

    def test_alibaba_open_code_reviewer_hardcoded_secrets(self):
        reviewer = AlibabaOpenCodeReviewer()
        diff = """--- a/config.py
+++ b/config.py
@@ -1,2 +1,3 @@
+api_key = "sk-live-0123456789abcdef0123"
"""
        report = reviewer.review_git_diff(diff)
        secrets = [f for f in report.findings if f.rule_id == "ALIBABA-SEC-002"]
        self.assertEqual(len(secrets), 1)

    def test_alibaba_open_code_reviewer_concurrency_race(self):
        reviewer = AlibabaOpenCodeReviewer()
        diff = """--- a/state.py
+++ b/state.py
@@ -1,2 +1,3 @@
 def increment():
+    global counter
     counter += 1
"""
        report = reviewer.review_git_diff(diff)
        conc = [f for f in report.findings if f.rule_id == "ALIBABA-CONC-001"]
        self.assertEqual(len(conc), 1)

    def test_alibaba_open_code_reviewer_resource_leak(self):
        reviewer = AlibabaOpenCodeReviewer()
        diff = """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def load_file():
+    f = open("data.txt", "r")
     return f.read()
"""
        report = reviewer.review_git_diff(diff)
        leaks = [f for f in report.findings if f.rule_id == "ALIBABA-RES-001"]
        self.assertEqual(len(leaks), 1)

    # --- 7. E2E Testing Suite Invariants ---

    def test_e2e_testing_suite_execution(self):
        tester = HyperGateE2ETester()
        results = tester.run_e2e_suite()
        self.assertTrue(results["all_tests_passed"])
        self.assertTrue(results["ssrf_blocked"])
        self.assertTrue(results["alibaba_sqli_detected"])
        self.assertEqual(results["status"], PaperclipTaskStatus.COMPLETED.value)

    # --- 8. Orchestrator & Native 370-Kernel Mounting ---

    def test_orchestrator_apex_ecosystem_tools_mounting(self):
        tools = self.orchestrator.supervisor.list_all_tools()
        names = [t.name for t in tools]
        self.assertIn("apex_agentic_memory", names)
        self.assertIn("apex_decision_shield", names)
        self.assertIn("apex_hft_orderbook", names)
        self.assertIn("apex_datacenter_pack", names)
        self.assertIn("apex_killswitch_interlock", names)

    # --- 9. CLI Execution Verification ---

    def test_cli_commands(self):
        from apex_hypergate.cli import cmd_benchmark, cmd_review, cmd_e2e_test
        class MockArgs:
            iterations = 10
            file = None

        self.assertEqual(cmd_benchmark(MockArgs()), 0)
        self.assertEqual(cmd_review(MockArgs()), 0)
        self.assertEqual(cmd_e2e_test(MockArgs()), 0)


if __name__ == "__main__":
    unittest.main()
