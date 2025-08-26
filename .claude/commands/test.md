# test

Run the test suite with detailed coverage report for $ARGUMENTS.

If no arguments provided, run all tests. Otherwise, run specific test file or directory.

```bash
pytest $ARGUMENTS --cov=src --cov-report=term-missing --cov-report=html -v
```

After running tests:
- Report coverage percentage
- List any uncovered lines
- Suggest additional tests if coverage is below 85%