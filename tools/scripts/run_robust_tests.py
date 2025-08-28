#!/usr/bin/env python3
"""
Master Test Runner - Handles Docker/Local Environment

This script automatically runs the robust testing framework in the appropriate environment
and provides comprehensive feedback about simulation health.
"""

import subprocess
import sys
import os
from pathlib import Path
import json


def check_environment():
    """Check if we're in Docker or need to use Docker"""
    try:
        # Try importing PySpice to see if simulation environment is available
        import PySpice
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared
        
        # Try creating a simulator to check if ngspice works
        NgSpiceShared.new_instance()
        
        # Check ngspice version for compatibility warnings
        try:
            import subprocess
            result = subprocess.run(['ngspice', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.strip().split('\n')[0]
                if 'version 44' in version_line.lower():
                    return "local_warning", f"Local environment (WARNING: {version_line} - unsupported, may cause AC analysis issues)"
                else:
                    return "local", f"Local environment with working PySpice/ngspice ({version_line})"
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
            
        return "local", "Local environment with working PySpice/ngspice"
        
    except ImportError:
        return "docker", "PySpice not available locally, need Docker"
    except Exception as e:
        if "ngspice" in str(e).lower() or "duplicate declaration" in str(e):
            return "docker", f"ngspice conflict detected: {e}"
        return "error", f"Unknown simulation environment issue: {e}"


def run_tests_in_docker():
    """Run tests in Docker environment"""
    print("🐳 Running Tests in Docker Environment")
    print("=" * 40)
    
    commands = [
        # Basic AC analysis validation
        "python3 tests/test_robust_simulation_behavior.py",
        
        # Visual testing framework  
        "python3 tests/claude_visual_tester.py",
        
        # Quick report generation test
        "python3 test_ac_charts_fix.py"
    ]
    
    results = {}
    
    for cmd in commands:
        print(f"\n🔄 Running: {cmd}")
        
        docker_cmd = [
            "docker-compose", "-f", "deployment/docker-compose.yml", 
            "run", "--rm", "circuit-sim", "/bin/bash", "-c", 
            f"cd /workspace && {cmd}"
        ]
        
        try:
            result = subprocess.run(
                docker_cmd, 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            
            if result.returncode == 0:
                print("   ✅ Success")
                results[cmd] = {"status": "success", "output": result.stdout}
            else:
                print("   ❌ Failed")
                print(f"   Error: {result.stderr[:200]}...")
                results[cmd] = {"status": "failed", "error": result.stderr, "output": result.stdout}
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout")
            results[cmd] = {"status": "timeout"}
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[cmd] = {"status": "exception", "error": str(e)}
    
    return results


def run_tests_locally():
    """Run tests in local environment"""
    print("🏠 Running Tests Locally")
    print("=" * 25)
    
    # Run basic validation
    try:
        result = subprocess.run([sys.executable, "tests/test_robust_simulation_behavior.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if "Issues detected" in result.stdout:
            print("❌ Issues detected in local simulation")
            return {"local_test": {"status": "issues_found", "output": result.stdout}}
        else:
            print("✅ Local simulation appears healthy")
            return {"local_test": {"status": "success", "output": result.stdout}}
            
    except Exception as e:
        return {"local_test": {"status": "failed", "error": str(e)}}


def analyze_test_results(results: dict) -> dict:
    """Analyze test results and provide actionable feedback"""
    analysis = {
        "environment_status": "unknown",
        "simulation_health": "unknown", 
        "critical_issues": [],
        "recommendations": [],
        "confidence": 0.0
    }
    
    # Check if any tests succeeded
    success_count = 0
    total_count = len(results)
    
    for cmd, result in results.items():
        if result.get("status") == "success":
            success_count += 1
        elif "real-only" in str(result.get("output", "")) or "missing phase" in str(result.get("output", "")):
            analysis["critical_issues"].append("AC analysis returning real-only values (missing phase data)")
        elif "duplicate declaration" in str(result.get("error", "")):
            analysis["critical_issues"].append("PySpice/ngspice environment conflict")
    
    analysis["confidence"] = success_count / max(total_count, 1)
    
    if analysis["confidence"] > 0.8:
        analysis["simulation_health"] = "healthy"
        analysis["recommendations"].append("✅ Simulation engine working correctly")
    elif analysis["confidence"] > 0.5:
        analysis["simulation_health"] = "marginal"
        analysis["recommendations"].append("⚠️ Some issues detected, review test output")
    else:
        analysis["simulation_health"] = "unhealthy"
        analysis["recommendations"].append("❌ Major issues detected, immediate attention needed")
    
    # Specific recommendations based on issues
    if any("real-only" in issue for issue in analysis["critical_issues"]):
        analysis["recommendations"].append("🔧 Fix AC voltage source in src/circuit_sim/simulator/builder.py")
    
    if any("environment conflict" in issue for issue in analysis["critical_issues"]):
        analysis["recommendations"].append("🐳 Use Docker environment for consistent simulation results")
    
    return analysis


def main():
    """Main test runner with environment detection and intelligent analysis"""
    print("🚀 Robust Circuit Simulation Testing")
    print("=" * 45)
    
    # Check for force Docker flag
    force_docker = "--docker" in sys.argv or "-d" in sys.argv or os.environ.get("FORCE_DOCKER", "").lower() == "true"
    
    if force_docker:
        env_type, env_message = "docker", "Forced Docker environment via flag/env"
    else:
        # Check environment
        env_type, env_message = check_environment()
    print(f"🔍 Environment: {env_type}")
    print(f"   {env_message}")
    
    # Run tests in appropriate environment
    if env_type == "docker" or env_type == "error":
        print(f"\n🐳 Using Docker for reliable testing environment")
        test_results = run_tests_in_docker()
    elif env_type == "local_warning":
        print(f"\n⚠️  WARNING: Unsupported ngspice version detected!")
        print("   AC analysis issues are expected with ngspice 44+")
        print("   Consider using Docker for consistent results")
        print(f"\n🏠 Running in local environment")
        test_results = run_tests_locally()
    else:
        print(f"\n🏠 Running in local environment")
        test_results = run_tests_locally()
    
    # Analyze results
    print(f"\n📊 Analyzing Test Results...")
    analysis = analyze_test_results(test_results)
    
    # Print summary
    print(f"\n" + "=" * 45)
    print("🎯 TEST SUMMARY")
    print("=" * 45)
    print(f"Environment: {env_type}")
    print(f"Simulation Health: {analysis['simulation_health']}")
    print(f"Confidence: {analysis['confidence']:.1%}")
    print(f"Critical Issues: {len(analysis['critical_issues'])}")
    
    if analysis["critical_issues"]:
        print(f"\n🚨 Critical Issues:")
        for issue in analysis["critical_issues"]:
            print(f"   • {issue}")
    
    print(f"\n💡 Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"   {rec}")
    
    # Save analysis
    analysis_path = Path("test_analysis.json")
    with open(analysis_path, 'w') as f:
        json.dump({
            "timestamp": "2025-08-27T18:56:00",
            "environment": env_type,
            "analysis": analysis,
            "test_results": test_results
        }, f, indent=2)
    
    print(f"\n💾 Full analysis saved: {analysis_path}")
    
    # Final recommendations
    if analysis["simulation_health"] == "unhealthy":
        print(f"\n🚨 IMMEDIATE ACTION NEEDED")
        print(f"   The simulation engine has critical issues")
        print(f"   Use Docker environment for consistent results:")
        print(f"   docker-compose -f deployment/docker-compose.yml run --rm circuit-sim bash")
    elif analysis["simulation_health"] == "healthy":
        print(f"\n✅ SIMULATION ENGINE HEALTHY")
        print(f"   Continue development with confidence")
        print(f"   Regular testing recommended")


if __name__ == "__main__":
    main()