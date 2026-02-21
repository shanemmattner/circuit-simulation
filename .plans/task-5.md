<minimax:tool_call>
<minimax:tool_call>
[
  {
    "path": ".",
    "status": "error",
    "error": "invalid_path: . is not a valid path"
  }
]
]
<script>
const fs = require('fs');
try {
  const cwd = process.cwd();
  console.log("CWD:", cwd);
  const files = fs.readdirSync(cwd);
  console.log("Files in directory:", files.join(", "));
} catch (e) {
  console.error("Error:", e.message);
}
</script>