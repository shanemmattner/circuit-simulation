I'll start by exploring the project structure to find circuit-related files.
<minimax:tool_call>
<invoke name="cli-mcp-server_run_command">
<parameter name="command">find . -type f -name "*.py" | head -50</parameter>
</invoke>
<invoke name="cli-mcp-server_run_command">
<parameter name="command">ls -la</parameter>
</invoke>
</minimax:tool_call>