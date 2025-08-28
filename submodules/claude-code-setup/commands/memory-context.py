"""
Memory Context Command

Universal command that provides project context through memory-bank-agent.
This is the CRITICAL first step in any session.

Usage: claude memory-context [--focus=area]
"""

import sys
import os
from pathlib import Path

def main():
    """Get memory bank context for session."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Get project context from memory bank")
    parser.add_argument("--focus", help="Focus area (api, testing, features, etc.)")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    # Import memory-bank-agent
    agents_dir = Path(__file__).parent.parent / "agents"
    sys.path.insert(0, str(agents_dir))
    
    try:
        from memory_bank_agent import MemoryBankAgent
        
        agent = MemoryBankAgent(args.project_root)
        context = agent.get_session_context(args.focus)
        print(context)
        
    except ImportError as e:
        print(f"❌ Error: Could not import memory-bank-agent: {e}")
        print("Make sure the agents are properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error getting context: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()