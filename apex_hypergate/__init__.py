"""Apex_HyperGate: Sovereign Zero-Latency AI Agent & MCP Gateway Daemon.

Universal reverse proxy, Alien's Trick token slasher, Nerve security sandbox,
Radix prefix KV-router, Hermes Paperclip Company OS adapter, and Alibaba Open Code Review.
"""

from apex_hypergate.core.primitives import (
    MCPToolSchema,
    SecurityVerdict,
    SecurityVerdictKind,
    PaperclipTask,
    PaperclipTaskStatus,
    CodeReviewFinding,
    CodeReviewReport,
    ReviewSeverity,
)
from apex_hypergate.core.aliens_trick_slasher import AliensTrickTokenSlasher
from apex_hypergate.core.nerve_sandbox import NerveSecuritySandbox
from apex_hypergate.core.radix_router import RadixPrefixKVRouter
from apex_hypergate.core.process_supervisor import MCPProcessSupervisor
from apex_hypergate.core.config_manager import ClientConfigManager
from apex_hypergate.adapters.paperclip_adapter import HermesPaperclipAdapter
from apex_hypergate.ocr.alibaba_reviewer import AlibabaOpenCodeReviewer
from apex_hypergate.eval.e2e_testing import HyperGateE2ETester
from apex_hypergate.orchestrator import ApexHyperGateOrchestrator

__version__ = "1.0.0"

__all__ = [
    "ApexHyperGateOrchestrator",
    "AliensTrickTokenSlasher",
    "NerveSecuritySandbox",
    "RadixPrefixKVRouter",
    "MCPProcessSupervisor",
    "ClientConfigManager",
    "HermesPaperclipAdapter",
    "AlibabaOpenCodeReviewer",
    "HyperGateE2ETester",
    "MCPToolSchema",
    "SecurityVerdict",
    "SecurityVerdictKind",
    "PaperclipTask",
    "PaperclipTaskStatus",
    "CodeReviewFinding",
    "CodeReviewReport",
    "ReviewSeverity",
]
