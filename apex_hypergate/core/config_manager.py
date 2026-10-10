"""Apex_HyperGate: Universal Multi-Client Auto-Configurator.

Detects and synchronizes MCP gateway client configurations across Cursor,
Claude Desktop, Claude Code, Windsurf, and VS Code in a single operation.
"""

import os
import json
from typing import Dict, List, Any


class ClientConfigManager:
    """Detects and updates client JSON configurations to route through Apex_HyperGate."""

    @staticmethod
    def get_client_config_paths() -> Dict[str, str]:
        """Return standardized configuration file paths across editors."""
        home = os.path.expanduser("~")
        return {
            "cursor": os.path.join(home, ".cursor", "mcp.json"),
            "claude_desktop_mac": os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json"),
            "claude_code": os.path.join(home, ".claude", "config.json"),
            "windsurf": os.path.join(home, ".codeium", "windsurf", "mcp_config.json"),
            "vscode": os.path.join(".vscode", "mcp.json"),
        }

    @staticmethod
    def generate_hypergate_client_block(port: int = 8000) -> Dict[str, Any]:
        """Generate client configuration pointing to local Apex_HyperGate daemon."""
        return {
            "apex-hypergate": {
                "command": "hypergate",
                "args": ["mcp-proxy", "--port", str(port)],
                "env": {
                    "APEX_HYPERGATE_ENDPOINT": f"http://127.0.0.1:{port}/v1"
                }
            }
        }

    def configure_client(self, config_file_path: str, port: int = 8000) -> bool:
        """Safely inject Apex_HyperGate into target client JSON config."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(config_file_path)), exist_ok=True)
            current_data: Dict[str, Any] = {}
            if os.path.exists(config_file_path):
                with open(config_file_path, "r", encoding="utf-8") as f:
                    try:
                        current_data = json.load(f)
                    except json.JSONDecodeError:
                        current_data = {}

            if "mcpServers" not in current_data:
                current_data["mcpServers"] = {}

            current_data["mcpServers"]["apex-hypergate"] = self.generate_hypergate_client_block(port)["apex-hypergate"]

            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=2)
            return True
        except Exception:
            return False

    def auto_configure_all(self, port: int = 8000) -> Dict[str, bool]:
        """Attempt configuration across all supported client targets."""
        results = {}
        paths = self.get_client_config_paths()
        for client_name, path in paths.items():
            results[client_name] = self.configure_client(path, port=port)
        return results
