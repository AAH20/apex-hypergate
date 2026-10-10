"""Apex_HyperGate: Foundational Data Contracts and Primitives.

Defines schemas for MCP tool definitions, security sandboxing verdicts,
Paperclip Company OS tasks, and Alibaba Open Code Review findings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import time
import hashlib
import json


class SecurityVerdictKind(str, Enum):
    """Nerve security inspection verdicts."""
    APPROVED = "APPROVED"
    BLOCKED_SSRF = "BLOCKED_SSRF"
    BLOCKED_PATH_TRAVERSAL = "BLOCKED_PATH_TRAVERSAL"
    BLOCKED_DESTRUCTIVE = "BLOCKED_DESTRUCTIVE"
    BLOCKED_INJECTION = "BLOCKED_INJECTION"


class PaperclipTaskStatus(str, Enum):
    """Paperclip Company OS task lifecycle states."""
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


class ReviewSeverity(str, Enum):
    """Alibaba Open Code Review issue severities."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class MCPToolSchema:
    """Tool definition exposed by native or external MCP servers."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str = "local"
    cost_tokens: int = 50
    relevance_score: float = 1.0

    @property
    def schema_hash(self) -> str:
        payload = f"{self.name}:{self.server_id}:{json.dumps(self.input_schema, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class SecurityVerdict:
    """Nerve sub-50us security inspection verdict."""
    verdict: SecurityVerdictKind
    reason: str
    latency_us: float = 0.0
    receipt_hash: str = ""
    is_safe: bool = True


@dataclass
class PaperclipTask:
    """Paperclip Company OS budget-governed task."""
    task_id: str
    title: str
    usd_budget: float
    consumed_usd: float = 0.0
    tokens_consumed: int = 0
    status: PaperclipTaskStatus = PaperclipTaskStatus.QUEUED
    heartbeat_count: int = 0
    created_at: float = field(default_factory=time.time)
    receipts: List[str] = field(default_factory=list)

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.usd_budget - self.consumed_usd)


@dataclass
class CodeReviewFinding:
    """Alibaba Open Code Review rule finding."""
    rule_id: str
    severity: ReviewSeverity
    file_path: str
    line_number: int
    message: str
    suggested_fix: str
    rule_category: str = "SECURITY"


@dataclass
class CodeReviewReport:
    """Alibaba Open Code Review evaluation result."""
    files_reviewed: int
    findings: List[CodeReviewFinding]
    review_latency_us: float
    passed_rule_checks: int
    total_rule_checks: int
    aacr_precision: float = 1.0
    aacr_recall: float = 1.0
