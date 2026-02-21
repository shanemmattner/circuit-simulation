<minimax:tool_call>
<invoke name="cli-mcp-server_run_command">
<parameter name="command">find /data -type f -name "*.py" | head -50</parameter>
</invoke>
<invoke name="cli-mcp-server_run_command">
<parameter name="command">ls -la /data</parameter>
</invoke>
</minimax:tool_call>