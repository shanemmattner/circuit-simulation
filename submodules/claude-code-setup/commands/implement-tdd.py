"""
Implement TDD Command

Universal command for Test-Driven Development implementation.
Enforces RED -> GREEN -> REFACTOR cycle.

Usage: claude implement-tdd [feature] [--prd=name] [--task=id]
"""

import sys
import os
from pathlib import Path

def main():
    """Implement feature using TDD."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Implement feature using Test-Driven Development")
    parser.add_argument("feature", nargs="?", help="Feature to implement")
    parser.add_argument("--prd", help="Associated PRD reference")
    parser.add_argument("--task", help="Work task ID")
    parser.add_argument("--cycle", help="Run single TDD cycle for specific test")
    parser.add_argument("--validate", nargs="+", help="Validate TDD compliance for files")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    # Import TDD implementer agent
    agents_dir = Path(__file__).parent.parent / "agents"
    sys.path.insert(0, str(agents_dir))
    
    try:
        from tdd_implementer import TDDImplementer
        
        implementer = TDDImplementer(args.project_root)
        
        if args.validate:
            print("🔍 Validating TDD compliance...")
            result = implementer.validate_tdd_compliance(args.validate)
            
            if result["compliant"]:
                print("✅ Code follows TDD principles")
                print(f"📊 Test coverage: {result['test_coverage']}%")
                print(f"🏆 Test quality: {result['test_quality']}")
            else:
                print("❌ TDD compliance issues found:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
                print(f"📊 Test coverage: {result['test_coverage']}%")
                sys.exit(1)
            return
        
        if args.cycle:
            print(f"🔄 Running TDD cycle: {args.cycle}")
            result = implementer.run_tdd_cycle(args.cycle)
            
            if result["success"]:
                print("✅ TDD cycle completed successfully")
                phases = result["phase_results"]
                print(f"🔴 RED: {phases['red'].get('test_written', 'N/A')}")
                print(f"🟢 GREEN: {phases['green'].get('implementation_added', 'N/A')}")
                print(f"🔵 REFACTOR: {phases['refactor'].get('refactoring_needed', 'N/A')}")
            else:
                print(f"❌ TDD cycle failed: {result.get('error')}")
                sys.exit(1)
            return
        
        # Full feature implementation
        if not args.feature:
            args.feature = input("Enter feature description: ")
        
        print("🔴🟢🔵 Starting TDD Feature Implementation")
        print("=" * 50)
        print("This will follow strict Test-Driven Development:")
        print("  🔴 RED: Write failing tests")
        print("  🟢 GREEN: Make tests pass with minimal code")
        print("  🔵 REFACTOR: Improve code while keeping tests green")
        print()
        
        # Check for PRD approval
        if args.prd:
            print(f"📄 Using PRD: {args.prd}")
            # TODO: Validate PRD is approved
        else:
            print("⚠️ No PRD specified - ensure requirements are clear")
            confirm = input("Continue without PRD? (y/n): ")
            if not confirm.lower().startswith('y'):
                print("❌ Implementation cancelled - create PRD first")
                sys.exit(1)
        
        result = implementer.implement_feature(args.feature, args.prd, args.task)
        
        if result["success"]:
            print("\n🎉 Feature Implementation Complete!")
            print(f"📁 Test file: {result['test_file']}")
            print(f"📁 Implementation file: {result['implementation_file']}")
            print(f"📊 Test cases: {result['test_cases_count']}")
            
            if result["patterns_learned"]:
                print(f"\n📚 Patterns Learned:")
                for pattern in result["patterns_learned"]:
                    print(f"  - {pattern}")
            
            print("\n✅ Ready for integration and deployment!")
        else:
            print(f"\n❌ Implementation failed: {result.get('error')}")
            if "details" in result:
                print(f"Details: {result['details']}")
            sys.exit(1)
        
    except ImportError as e:
        print(f"❌ Error: Could not import tdd-implementer: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error implementing feature: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()