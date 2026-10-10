"""Apex_HyperGate: Hermes Paperclip Company OS Adapter.

Integrates Nous Research Hermes Agent with Paperclip Company OS
(@paperclipai/hermes-paperclip-adapter): budget governance, multi-heartbeat task queues,
and ActionLedger cryptographic audit receipt generation.
"""

import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from apex_hypergate.core.primitives import (
    PaperclipTask,
    PaperclipTaskStatus,
)


class HermesPaperclipAdapter:
    """Turnkey Paperclip Company OS adapter for Hermes Agent."""

    # Pricing per token (Blended late 2026 frontier inference rates)
    PROMPT_TOKEN_RATE_USD = 0.000003     # $3.00 per 1M tokens
    COMPLETION_TOKEN_RATE_USD = 0.000015 # $15.00 per 1M tokens

    def __init__(self):
        # task_id -> PaperclipTask
        self._tasks: Dict[str, PaperclipTask] = {}

    def create_task(self, task_id: str, title: str, usd_budget: float = 5.0) -> PaperclipTask:
        """Initialize a new budget-governed Paperclip task."""
        task = PaperclipTask(
            task_id=task_id,
            title=title,
            usd_budget=usd_budget,
            status=PaperclipTaskStatus.QUEUED,
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[PaperclipTask]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)

    def heartbeat_tick(
        self,
        task_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        tool_action_name: Optional[str] = None,
        tool_payload: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, PaperclipTask, Optional[str]]:
        """Process one agentic heartbeat tick, accounting for USD budget and emitting ActionLedger receipt.
        
        Returns:
            (can_proceed, updated_task, failure_reason)
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found in Paperclip registry")

        if task.status == PaperclipTaskStatus.BUDGET_EXCEEDED:
            return False, task, "Task already marked BUDGET_EXCEEDED"

        # Calculate incremental USD cost
        step_cost = (prompt_tokens * self.PROMPT_TOKEN_RATE_USD) + (completion_tokens * self.COMPLETION_TOKEN_RATE_USD)
        
        if task.consumed_usd + step_cost > task.usd_budget:
            task.status = PaperclipTaskStatus.BUDGET_EXCEEDED
            receipt = self._emit_action_receipt(task_id, "BUDGET_EXCEEDED", {"step_cost": step_cost})
            task.receipts.append(receipt)
            return False, task, f"Budget exceeded: {task.consumed_usd + step_cost:.4f} > {task.usd_budget:.4f} USD"

        # Update budget and tokens
        task.consumed_usd = round(task.consumed_usd + step_cost, 6)
        task.tokens_consumed += (prompt_tokens + completion_tokens)
        task.heartbeat_count += 1
        task.status = PaperclipTaskStatus.IN_PROGRESS

        # Emit ActionLedger cryptographic receipt
        action_payload = tool_payload or {"action": tool_action_name or "REASONING_TICK"}
        receipt = self._emit_action_receipt(task_id, tool_action_name or "HEARTBEAT", action_payload)
        task.receipts.append(receipt)

        return True, task, None

    def mark_task_complete(self, task_id: str) -> PaperclipTask:
        """Transition task to COMPLETED and emit final closure receipt."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        task.status = PaperclipTaskStatus.COMPLETED
        receipt = self._emit_action_receipt(task_id, "TASK_COMPLETED", {"total_consumed_usd": task.consumed_usd})
        task.receipts.append(receipt)
        return task

    def _emit_action_receipt(self, task_id: str, action: str, payload: Dict[str, Any]) -> str:
        """Emit an immutable SHA-256 ActionLedger receipt."""
        raw = f"PAPERCLIP:{task_id}:{action}:{sorted(str(payload.items()))}:{time.time()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
