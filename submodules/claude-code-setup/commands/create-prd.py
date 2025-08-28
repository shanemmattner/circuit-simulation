"""
Create PRD Command

Universal command for creating Product Requirements Documents.
Ensures no code is written without approved PRD.

Usage: claude create-prd [feature-description]
"""

import sys
import os
from pathlib import Path

def main():
    """Create or refine a PRD."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create or refine Product Requirements Document")
    parser.add_argument("feature", nargs="?", help="Feature description for new PRD")
    parser.add_argument("--refine", help="Name of existing PRD to refine")
    parser.add_argument("--list", action="store_true", help="List available PRDs")
    parser.add_argument("--validate", help="Validate PRD completeness")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    # Import PRD creator agent
    agents_dir = Path(__file__).parent.parent / "agents"
    sys.path.insert(0, str(agents_dir))
    
    try:
        from prd_creator import PRDCreator
        
        creator = PRDCreator(args.project_root)
        
        if args.list:
            prds = creator.list_prds()
            if prds:
                print("📋 Available PRDs:")
                for prd in prds:
                    status_emoji = {"Draft": "📝", "Approved": "✅", "In Progress": "🚧"}.get(prd["status"], "❓")
                    print(f"  {status_emoji} {prd['name']} - {prd['status']} ({prd['modified']})")
            else:
                print("No PRDs found")
            return
        
        if args.validate:
            is_complete, missing = creator.validate_prd_completeness(args.validate)
            if is_complete:
                print(f"✅ PRD '{args.validate}' is complete and ready for implementation")
            else:
                print(f"❌ PRD '{args.validate}' is incomplete")
                print(f"Missing sections: {', '.join(missing)}")
            return
        
        if args.refine:
            try:
                prd_file = creator.refine_existing_prd(args.refine)
                print(f"✅ PRD refined: {prd_file}")
            except FileNotFoundError:
                print(f"❌ PRD not found: {args.refine}")
                sys.exit(1)
            return
        
        # Create new PRD
        if not args.feature:
            args.feature = input("Enter feature description: ")
        
        print("🚀 Creating new PRD through interactive collaboration...")
        print("This ensures we build exactly what you need.\n")
        
        prd_file = creator.create_interactive_prd(args.feature)
        print(f"\n✅ PRD created: {prd_file}")
        print("\n🔒 Remember: No code implementation without PRD approval!")
        
    except ImportError as e:
        print(f"❌ Error: Could not import prd-creator: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating PRD: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()