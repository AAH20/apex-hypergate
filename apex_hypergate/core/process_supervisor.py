"""Apex_HyperGate: Tool Registry (process-supervisor scaffold).

NOTE: despite the class name, this module does not spawn or manage subprocesses. It is an
in-memory registry of native tool schemas plus a placeholder for external server metadata.
`subprocess` is imported but unused; there is no I/O, health-check ping, auto-restart, or
orphan handling. See the README Roadmap.
"""

import subprocess
import time
import json
from typing import Dict, List, Optional, Any
from apex_hypergate.core.primitives import MCPToolSchema


class MCPProcessSupervisor:
    """In-memory tool-schema registry with a placeholder for external server metadata."""

    def __init__(self):
        # server_id -> metadata dictionary
        self._servers: Dict[str, Dict[str, Any]] = {}
        # tool_name -> MCPToolSchema
        self._tools: Dict[str, MCPToolSchema] = {}

    def register_native_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        server_id: str = "native",
        cost_tokens: int = 40,
    ) -> MCPToolSchema:
        """Register an in-process native tool schema (schema only; no execution backend)."""
        tool = MCPToolSchema(
            name=name,
            description=description,
            input_schema=input_schema,
            server_id=server_id,
            cost_tokens=cost_tokens,
        )
        self._tools[name] = tool
        return tool

    def register_server(self, server_id: str, command: str, args: List[str]) -> Dict[str, Any]:
        """Record metadata for an external MCP server (does not start a process)."""
        self._servers[server_id] = {
            "server_id": server_id,
            "command": command,
            "args": args,
            "status": "RUNNING",
            "registered_at": time.time(),
            "restart_count": 0,
        }
        return self._servers[server_id]

    def list_all_tools(self) -> List[MCPToolSchema]:
        """Return all registered native and external tools."""
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[MCPToolSchema]:
        """Retrieve tool schema by name."""
        return self._tools.get(name)

    def heartbeat_health_check(self) -> Dict[str, str]:
        """Return the recorded status of each registered server (no live probe is sent)."""
        status_map = {}
        for s_id, s_meta in self._servers.items():
            # In a real environment, send ping frame over stdio pipe
            status_map[s_id] = s_meta["status"]
        return status_map

    def shutdown_all(self) -> int:
        """Mark all registered servers STOPPED and clear the registry (no processes are terminated)."""
        count = len(self._servers)
        for s_id, s_meta in self._servers.items():
            s_meta["status"] = "STOPPED"
        self._servers.clear()
        return count
