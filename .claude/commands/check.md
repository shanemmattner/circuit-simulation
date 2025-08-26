# check

Run all quality checks on the codebase before committing.

Execute the following commands in sequence:
1. Format code with black
2. Lint with ruff
3. Type check with mypy
4. Run all tests with coverage

```bash
black src/ tests/ examples/
ruff check src/ tests/ examples/
mypy src/ --strict
pytest --cov=src --cov-report=term-missing
```

Report any issues found and suggest fixes.