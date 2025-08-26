# ship

Prepare code for PR by running all quality checks and showing git status.

Steps:
1. Format all Python code with black
2. Run linting checks with ruff
3. Verify type hints with mypy
4. Execute test suite with coverage
5. Show git status for review

```bash
black src/ tests/ examples/
ruff check src/ tests/ examples/
mypy src/ --strict  
pytest -v
git status
```

If all checks pass, the code is ready to commit and push.