"""Apex_HyperGate: Unified Master Gateway Orchestrator.

Coordinates proxy routing, Alien's Trick token slashing, Nerve security sandboxing,
Radix prefix KV-cache routing, Hermes Paperclip Company OS budget governance,
and Alibaba Open Code Review deterministic Git diff analysis.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from apex_hypergate.core.primitives import (
    MCPToolSchema,
    SecurityVerdict,
    CodeReviewReport,
    PaperclipTask,
)
from apex_hypergate.core.aliens_trick_slasher import AliensTrickTokenSlasher
from apex_hypergate.core.nerve_sandbox import NerveSecuritySandbox
from apex_hypergate.core.radix_router import RadixPrefixKVRouter
from apex_hypergate.core.process_supervisor import MCPProcessSupervisor
from apex_hypergate.core.config_manager import ClientConfigManager
from apex_hypergate.adapters.paperclip_adapter import HermesPaperclipAdapter
from apex_hypergate.ocr.alibaba_reviewer import AlibabaOpenCodeReviewer


class ApexHyperGateOrchestrator:
    """Master OS Gateway coordinating multi-client proxying, security, and verification."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.slasher = AliensTrickTokenSlasher()
        self.sandbox = NerveSecuritySandbox(workspace_root=workspace_root)
        self.router = RadixPrefixKVRouter()
        self.supervisor = MCPProcessSupervisor()
        self.config_manager = ClientConfigManager()
        self.paperclip = HermesPaperclipAdapter()
        self.reviewer = AlibabaOpenCodeReviewer()
        
        # Auto-mount native tools from the 370-kernel Apex ecosystem
        self._mount_apex_ecosystem_tools()

    def _mount_apex_ecosystem_tools(self) -> None:
        """Mount native deep-tech tools from Ahmed's 370-kernel portfolio."""
        self.supervisor.register_native_tool(
            name="apex_agentic_memory",
            description="Query bi-temporal knowledge graph, Claude-Mem observations, and Hindsight reflections",
            input_schema={"query": {"type": "string"}, "token_budget": {"type": "integer"}},
            server_id="apex:memory",
            cost_tokens=45,
        )
        self.supervisor.register_native_tool(
            name="apex_decision_shield",
            description="Verify kinematic control actions using closed-form CBF-QP safety barriers",
            input_schema={"action_id": {"type": "string"}, "velocity_vector": {"type": "array"}},
            server_id="apex:decision",
            cost_tokens=50,
        )
        self.supervisor.register_native_tool(
            name="apex_hft_orderbook",
            description="Execute microsecond L3 limit order book matching and cross-venue SOR simulation",
            input_schema={"symbol": {"type": "string"}, "order_type": {"type": "string"}, "price": {"type": "number"}},
            server_id="apex:hft",
            cost_tokens=40,
        )
        self.supervisor.register_native_tool(
            name="apex_datacenter_pack",
            description="Multi-dimensional vector bin packing and thermal rack cooling optimization",
            input_schema={"gpu_demands": {"type": "array"}, "power_budget_kw": {"type": "number"}},
            server_id="apex:datacenter",
            cost_tokens=55,
        )
        self.supervisor.register_native_tool(
            name="apex_killswitch_interlock",
            description="Sub-15ms protection relay coordination and DVFS power-shedding trip defuser",
            input_schema={"bus_voltage_kv": {"type": "number"}, "frequency_hz": {"type": "number"}},
            server_id="apex:killswitch",
            cost_tokens=35,
        )

    def route_and_slash_tools(
        self,
        user_query: str,
        token_budget: int = 2500,
        session_id: str = "GLOBAL",
    ) -> Tuple[List[MCPToolSchema], Dict[str, Any]]:
        """Prune tool schemas under budget and serialize with canonical KV-cache prefix."""
        all_tools = self.supervisor.list_all_tools()
        pruned_tools, metrics = self.slasher.prune_tool_schemas(all_tools, user_query, token_budget=token_budget)
        
        # Enforce canonical ordering and update Radix Trie
        canonical_tools = self.router.canonicalize_tool_schemas(pruned_tools)
        canonical_json = self.router.serialize_canonical_prompt_block(canonical_tools)
        kv_hit = self.router.record_and_route_prefix(session_id, canonical_json)
        
        metrics["kv_cache_hit"] = kv_hit
        metrics["cache_affinity_rate"] = self.router.cache_affinity_rate
        return canonical_tools, metrics

    def inspect_and_authorize_tool(self, tool_name: str, arguments: Dict[str, Any]) -> SecurityVerdict:
        """Run Nerve sub-50us security firewall checks."""
        return self.sandbox.inspect_tool_call(tool_name, arguments)

    def review_code_diff(self, diff_text: str) -> CodeReviewReport:
        """Execute Alibaba Open Code Review on code diff."""
        return self.reviewer.review_git_diff(diff_text)

    def benchmark_gateway_latencies(self, iterations: int = 100) -> Dict[str, float]:
        """Profile microsecond execution latencies across all subsystems."""
        # 1. Nerve Security Inspection
        nerve_times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            self.sandbox.inspect_tool_call("view_file", {"path": "src/main.py"})
            nerve_times.append((time.perf_counter_ns() - start) / 1000.0)

        # 2. Alien's Trick Token Slasher
        all_tools = self.supervisor.list_all_tools()
        slasher_times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            self.slasher.prune_tool_schemas(all_tools, "database memory optimization", token_budget=150)
            slasher_times.append((time.perf_counter_ns() - start) / 1000.0)

        # 3. Alibaba Open Code Reviewer
        mock_diff = "+++ b/test.py\n+cursor.execute(f'SELECT * FROM x WHERE id={y}')"
        ocr_times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            self.reviewer.review_git_diff(mock_diff)
            ocr_times.append((time.perf_counter_ns() - start) / 1000.0)

        # 4. Radix Trie Router
        router_times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            self.router.canonicalize_tool_schemas(all_tools)
            router_times.append((time.perf_counter_ns() - start) / 1000.0)

        return {
            "nerve_sandbox_avg_us": round(sum(nerve_times) / len(nerve_times), 2),
            "aliens_trick_slasher_avg_us": round(sum(slasher_times) / len(slasher_times), 2),
            "alibaba_ocr_avg_us": round(sum(ocr_times) / len(ocr_times), 2),
            "radix_router_avg_us": round(sum(router_times) / len(router_times), 2),
        }
