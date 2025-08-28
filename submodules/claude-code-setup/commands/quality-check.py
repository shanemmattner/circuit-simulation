"""
Quality Check Command

Universal command for comprehensive code quality validation.
Runs all quality checks before commits and releases.

Usage: claude quality-check [--fix] [--coverage] [--security]
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Run comprehensive quality checks."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive code quality checks")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    parser.add_argument("--coverage", action="store_true", help="Run test coverage analysis")
    parser.add_argument("--security", action="store_true", help="Run security analysis")
    parser.add_argument("--format-only", action="store_true", help="Only run formatting")
    parser.add_argument("--lint-only", action="store_true", help="Only run linting")
    parser.add_argument("--test-only", action="store_true", help="Only run tests")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root)
    os.chdir(project_root)
    
    print("🔍 Universal Quality Check")
    print("=" * 40)
    
    # Detect project type and tools
    project_config = detect_project_config(project_root)
    
    print(f"📁 Project: {project_root.name}")
    print(f"🔧 Language: {project_config['language']}")
    print(f"🧪 Test Framework: {project_config['test_framework']}")
    print()
    
    results = {
        "formatting": None,
        "linting": None,
        "type_checking": None,
        "testing": None,
        "coverage": None,
        "security": None
    }
    
    # 1. Code Formatting
    if not args.lint_only and not args.test_only:
        print("🎨 Code Formatting")
        print("-" * 20)
        results["formatting"] = run_formatting(project_config, args.fix)
    
    # 2. Linting
    if not args.format_only and not args.test_only:
        print("\n🔍 Linting")
        print("-" * 20)
        results["linting"] = run_linting(project_config, args.fix)
    
    # 3. Type Checking
    if not args.format_only and not args.test_only and project_config["type_checker"]:
        print("\n📝 Type Checking")
        print("-" * 20)
        results["type_checking"] = run_type_checking(project_config)
    
    # 4. Testing
    if not args.format_only and not args.lint_only:
        print("\n🧪 Testing")
        print("-" * 20)
        results["testing"] = run_tests(project_config)
    
    # 5. Coverage Analysis
    if args.coverage or (not args.format_only and not args.lint_only):
        print("\n📊 Test Coverage")
        print("-" * 20)
        results["coverage"] = run_coverage_analysis(project_config)
    
    # 6. Security Analysis
    if args.security:
        print("\n🛡️ Security Analysis")
        print("-" * 20)
        results["security"] = run_security_analysis(project_config)
    
    # Summary
    print_summary(results)

def detect_project_config(project_root: Path) -> dict:
    """Detect project configuration from files."""
    config = {
        "language": "python",  # default
        "formatter": None,
        "linter": None,
        "type_checker": None,
        "test_framework": None
    }
    
    # Check for Python
    if (project_root / "pyproject.toml").exists() or \
       (project_root / "setup.py").exists() or \
       (project_root / "requirements.txt").exists():
        config["language"] = "python"
        config["formatter"] = "black"
        config["linter"] = "ruff"
        config["type_checker"] = "mypy"
        config["test_framework"] = "pytest"
    
    # Check for Node.js
    elif (project_root / "package.json").exists():
        config["language"] = "javascript"
        config["formatter"] = "prettier"
        config["linter"] = "eslint"
        config["type_checker"] = "tsc" if (project_root / "tsconfig.json").exists() else None
        config["test_framework"] = "jest"
    
    # Check for Go
    elif (project_root / "go.mod").exists():
        config["language"] = "go"
        config["formatter"] = "gofmt"
        config["linter"] = "golint"
        config["test_framework"] = "go test"
    
    # Check for Rust
    elif (project_root / "Cargo.toml").exists():
        config["language"] = "rust"
        config["formatter"] = "rustfmt"
        config["linter"] = "clippy"
        config["test_framework"] = "cargo test"
    
    # Override with CLAUDE.md settings if available
    claude_md = project_root / "CLAUDE.md"
    if claude_md.exists():
        try:
            content = claude_md.read_text().lower()
            
            # Extract formatter
            if "black" in content:
                config["formatter"] = "black"
            elif "prettier" in content:
                config["formatter"] = "prettier"
            
            # Extract linter
            if "ruff" in content:
                config["linter"] = "ruff"
            elif "eslint" in content:
                config["linter"] = "eslint"
            elif "pylint" in content:
                config["linter"] = "pylint"
            
            # Extract test framework
            if "pytest" in content:
                config["test_framework"] = "pytest"
            elif "jest" in content:
                config["test_framework"] = "jest"
        except Exception:
            pass
    
    return config

def run_command(cmd: list, description: str) -> dict:
    """Run a command and return results."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        success = result.returncode == 0
        return {
            "success": success,
            "output": result.stdout,
            "error": result.stderr,
            "description": description
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Command timed out: {' '.join(cmd)}",
            "description": description
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "description": description
        }

def run_formatting(config: dict, fix: bool) -> dict:
    """Run code formatting."""
    formatter = config["formatter"]
    
    if not formatter:
        return {"success": True, "skipped": True, "reason": "No formatter configured"}
    
    if formatter == "black":
        cmd = ["python", "-m", "black"]
        if not fix:
            cmd.append("--check")
        cmd.extend([".", "--exclude", "/(\.git|\.venv|venv|__pycache__)/"])
        
    elif formatter == "prettier":
        cmd = ["npx", "prettier"]
        if fix:
            cmd.append("--write")
        else:
            cmd.append("--check")
        cmd.append(".")
        
    elif formatter == "gofmt":
        if fix:
            cmd = ["gofmt", "-w", "."]
        else:
            cmd = ["gofmt", "-d", "."]
        
    elif formatter == "rustfmt":
        cmd = ["cargo", "fmt"]
        if not fix:
            cmd.append("--check")
    else:
        return {"success": False, "error": f"Unknown formatter: {formatter}"}
    
    result = run_command(cmd, f"Formatting with {formatter}")
    
    if result["success"]:
        if fix:
            print(f"✅ Code formatted with {formatter}")
        else:
            print(f"✅ Code formatting is correct ({formatter})")
    else:
        if fix:
            print(f"❌ Failed to format code with {formatter}")
        else:
            print(f"❌ Code formatting issues found ({formatter})")
        if result["error"]:
            print(f"   Error: {result['error'][:200]}")
    
    return result

def run_linting(config: dict, fix: bool) -> dict:
    """Run code linting."""
    linter = config["linter"]
    
    if not linter:
        return {"success": True, "skipped": True, "reason": "No linter configured"}
    
    if linter == "ruff":
        cmd = ["python", "-m", "ruff", "check", "."]
        if fix:
            cmd.append("--fix")
        
    elif linter == "pylint":
        cmd = ["python", "-m", "pylint", "."]
        
    elif linter == "eslint":
        cmd = ["npx", "eslint", "."]
        if fix:
            cmd.append("--fix")
            
    elif linter == "golint":
        cmd = ["golint", "./..."]
        
    elif linter == "clippy":
        cmd = ["cargo", "clippy", "--", "-D", "warnings"]
    else:
        return {"success": False, "error": f"Unknown linter: {linter}"}
    
    result = run_command(cmd, f"Linting with {linter}")
    
    if result["success"]:
        print(f"✅ No linting issues found ({linter})")
    else:
        print(f"❌ Linting issues found ({linter})")
        if result["output"]:
            # Show first few issues
            lines = result["output"].split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
    
    return result

def run_type_checking(config: dict) -> dict:
    """Run type checking."""
    type_checker = config["type_checker"]
    
    if not type_checker:
        return {"success": True, "skipped": True, "reason": "No type checker configured"}
    
    if type_checker == "mypy":
        cmd = ["python", "-m", "mypy", ".", "--strict"]
        
    elif type_checker == "tsc":
        cmd = ["npx", "tsc", "--noEmit"]
    else:
        return {"success": False, "error": f"Unknown type checker: {type_checker}"}
    
    result = run_command(cmd, f"Type checking with {type_checker}")
    
    if result["success"]:
        print(f"✅ No type errors found ({type_checker})")
    else:
        print(f"❌ Type errors found ({type_checker})")
        if result["output"]:
            # Show first few errors
            lines = result["output"].split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
    
    return result

def run_tests(config: dict) -> dict:
    """Run tests."""
    test_framework = config["test_framework"]
    
    if not test_framework:
        return {"success": True, "skipped": True, "reason": "No test framework configured"}
    
    if test_framework == "pytest":
        cmd = ["python", "-m", "pytest", "-v"]
        
    elif test_framework == "jest":
        cmd = ["npx", "jest"]
        
    elif test_framework == "go test":
        cmd = ["go", "test", "./..."]
        
    elif test_framework == "cargo test":
        cmd = ["cargo", "test"]
    else:
        return {"success": False, "error": f"Unknown test framework: {test_framework}"}
    
    result = run_command(cmd, f"Testing with {test_framework}")
    
    if result["success"]:
        # Extract test count from output
        output = result["output"]
        if "passed" in output.lower():
            print(f"✅ All tests passed ({test_framework})")
        else:
            print(f"✅ Tests completed successfully ({test_framework})")
    else:
        print(f"❌ Tests failed ({test_framework})")
        if result["output"]:
            # Show test failures
            lines = result["output"].split('\n')
            failure_lines = [line for line in lines if "FAILED" in line or "failed" in line.lower()][:5]
            for line in failure_lines:
                print(f"   {line}")
    
    return result

def run_coverage_analysis(config: dict) -> dict:
    """Run test coverage analysis."""
    if config["test_framework"] == "pytest":
        cmd = ["python", "-m", "pytest", "--cov=src", "--cov=.", "--cov-report=term-missing"]
        
    elif config["test_framework"] == "jest":
        cmd = ["npx", "jest", "--coverage"]
        
    elif config["test_framework"] == "go test":
        cmd = ["go", "test", "-cover", "./..."]
        
    elif config["test_framework"] == "cargo test":
        # Requires cargo-tarpaulin
        cmd = ["cargo", "tarpaulin", "--out", "Stdout"]
    else:
        return {"success": True, "skipped": True, "reason": "Coverage not configured"}
    
    result = run_command(cmd, "Test coverage analysis")
    
    if result["success"]:
        # Extract coverage percentage
        output = result["output"]
        import re
        
        coverage_patterns = [
            r'TOTAL.*?(\d+)%',
            r'Coverage: (\d+)%',
            r'coverage: (\d+\.?\d*)%'
        ]
        
        coverage_percentage = 0
        for pattern in coverage_patterns:
            match = re.search(pattern, output)
            if match:
                coverage_percentage = float(match.group(1))
                break
        
        if coverage_percentage >= 85:
            print(f"✅ Test coverage: {coverage_percentage}% (target: 85%+)")
        elif coverage_percentage >= 70:
            print(f"⚠️ Test coverage: {coverage_percentage}% (target: 85%+)")
        else:
            print(f"❌ Test coverage: {coverage_percentage}% (target: 85%+)")
        
        result["coverage_percentage"] = coverage_percentage
    else:
        print("❌ Coverage analysis failed")
        if result["error"]:
            print(f"   Error: {result['error'][:200]}")
    
    return result

def run_security_analysis(config: dict) -> dict:
    """Run security analysis."""
    if config["language"] == "python":
        # Run bandit for Python
        result1 = run_command(
            ["python", "-m", "bandit", "-r", ".", "-x", "tests/,test/"],
            "Security analysis with bandit"
        )
        
        # Run safety for dependency vulnerabilities
        result2 = run_command(
            ["python", "-m", "safety", "check"],
            "Dependency vulnerability check with safety"
        )
        
        if result1["success"] and result2["success"]:
            print("✅ No security issues found")
            return {"success": True, "bandit": result1, "safety": result2}
        else:
            print("❌ Security issues found")
            return {"success": False, "bandit": result1, "safety": result2}
            
    elif config["language"] == "javascript":
        # Run npm audit
        result = run_command(["npm", "audit"], "Security audit with npm")
        
        if result["success"]:
            print("✅ No security vulnerabilities found")
        else:
            print("❌ Security vulnerabilities found")
        
        return result
    
    else:
        return {"success": True, "skipped": True, "reason": "Security analysis not configured for this language"}

def print_summary(results: dict):
    """Print quality check summary."""
    print("\n" + "=" * 50)
    print("📊 QUALITY CHECK SUMMARY")
    print("=" * 50)
    
    total_checks = 0
    passed_checks = 0
    
    for check_name, result in results.items():
        if result is None:
            continue
            
        total_checks += 1
        
        if result.get("skipped"):
            print(f"⏭️  {check_name.title()}: Skipped ({result.get('reason', 'Unknown')})")
            continue
        
        if result["success"]:
            passed_checks += 1
            print(f"✅ {check_name.title()}: Passed")
            
            # Show coverage percentage if available
            if check_name == "coverage" and "coverage_percentage" in result:
                print(f"   Coverage: {result['coverage_percentage']}%")
        else:
            print(f"❌ {check_name.title()}: Failed")
            if result.get("error"):
                print(f"   Error: {result['error'][:100]}...")
    
    print(f"\nResult: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 All quality checks passed! Ready for commit/deploy.")
        sys.exit(0)
    else:
        print("❌ Some quality checks failed. Please fix issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()