"""
Optimize Prompt Command

Universal command for crafting optimal prompts for development tasks.
Improves outcomes by providing context-rich, targeted prompts.

Usage: claude optimize-prompt [task] [--agent=target] [--type=optimization]
"""

import sys
import os
from pathlib import Path

def main():
    """Optimize prompt for development task."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimize prompt for development tasks")
    parser.add_argument("task", nargs="?", help="Task description to optimize prompt for")
    parser.add_argument("--agent", default="tdd-implementer", 
                       help="Target agent (tdd-implementer, work-planner, etc.)")
    parser.add_argument("--type", choices=["tdd", "planning", "debugging", "general"],
                       help="Optimization type")
    parser.add_argument("--prd-context", help="PRD content to include in prompt")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    # Import prompt optimizer agent
    agents_dir = Path(__file__).parent.parent / "agents"
    sys.path.insert(0, str(agents_dir))
    
    try:
        from prompt_optimizer import PromptOptimizer
        
        optimizer = PromptOptimizer(args.project_root)
        
        if not args.task:
            args.task = input("Enter task description: ")
        
        print("🔧 Optimizing prompt for maximum effectiveness...")
        print(f"Task: {args.task}")
        print(f"Target Agent: {args.agent}")
        if args.type:
            print(f"Optimization Type: {args.type}")
        print()
        
        # Generate optimized prompt based on type
        if args.type == "tdd":
            optimized_prompt = optimizer.optimize_for_tdd(args.task, args.prd_context)
        elif args.type == "planning":
            optimized_prompt = optimizer.optimize_for_planning(args.task)
        elif args.type == "debugging":
            # Extract error info if provided
            error_info = input("Enter error information (optional): ").strip()
            optimized_prompt = optimizer.optimize_for_debugging(args.task, error_info or None)
        else:
            # General optimization
            optimized_prompt = optimizer.optimize_prompt(args.task, args.agent)
        
        print("✅ Optimized Prompt Generated")
        print("=" * 60)
        print(optimized_prompt)
        print("=" * 60)
        
        # Option to save prompt
        save_prompt = input("\nSave optimized prompt to file? (y/n): ").lower()
        if save_prompt.startswith('y'):
            prompt_filename = args.task.lower().replace(' ', '_')[:30] + "_prompt.md"
            prompt_file = Path(args.project_root) / "memory-bank" / "prompts" / prompt_filename
            prompt_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(prompt_file, 'w') as f:
                f.write(f"# Optimized Prompt for: {args.task}\n\n")
                f.write(f"**Generated**: {args.agent} agent\n")
                f.write(f"**Type**: {args.type or 'general'}\n")
                f.write(f"**Date**: {optimizer._get_project_context()}\n\n")
                f.write(optimized_prompt)
            
            print(f"📁 Prompt saved to: {prompt_file}")
        
        print("\n🚀 Ready to use this optimized prompt with your target agent!")
        
    except ImportError as e:
        print(f"❌ Error: Could not import prompt-optimizer: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error optimizing prompt: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()