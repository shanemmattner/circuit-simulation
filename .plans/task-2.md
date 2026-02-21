<minimax:tool_call>
<invoke name="cli-mcp-server_run_command">
<parameter name="command">find . -type f -name "*.rs" | head -50</parameter>
</invoke>
<invoke name="cli-mcp-server_run_command">
<parameter name="command">ls -la</parameter>
</invoke>
</minimax:tool_call>