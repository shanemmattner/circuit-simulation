"""
Plan Work Command

Universal command for intelligent work planning and task breakdown.
Breaks complex goals into manageable, testable chunks.

Usage: claude plan-work [goal] [--prd=name] [--complexity=level]
"""

import sys
import os
from pathlib import Path

def main():
    """Plan work for a goal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Plan work with intelligent task breakdown")
    parser.add_argument("goal", nargs="?", help="Goal to plan work for")
    parser.add_argument("--prd", help="Associated PRD name")
    parser.add_argument("--complexity", choices=["low", "medium", "high"], 
                       default="medium", help="Expected complexity")
    parser.add_argument("--breakdown", help="Break down specific task")
    parser.add_argument("--progress", help="Track progress on work plan")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    # Import work planner agent
    agents_dir = Path(__file__).parent.parent / "agents"
    sys.path.insert(0, str(agents_dir))
    
    try:
        from work_planner import WorkPlanner
        
        planner = WorkPlanner(args.project_root)
        
        if args.breakdown:
            print(f"🔨 Breaking down task: {args.breakdown}")
            subtasks = planner.break_down_task(args.breakdown)
            print(f"\n✅ Broke down into {len(subtasks)} subtasks:")
            for i, subtask in enumerate(subtasks, 1):
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(subtask.priority.value, "🟡")
                print(f"  {i}. {emoji} {subtask.title} ({subtask.estimated_minutes}min)")
            return
        
        if args.progress:
            try:
                progress = planner.track_progress(args.progress)
                print(f"📊 Progress for {args.progress}:")
                print(f"  Completion: {progress['completion_percentage']:.1f}%")
                print(f"  Tasks: {progress['tasks_completed']}/{progress['tasks_total']}")
                print(f"  Time: {progress['hours_completed']:.1f}/{progress['hours_total']:.1f} hours")
                
                if progress['tasks_blocked'] > 0:
                    print(f"  ⚠️ Blocked tasks: {progress['tasks_blocked']}")
                
                next_tasks = progress.get('next_available_tasks', [])
                if next_tasks:
                    print(f"\n🎯 Next available tasks:")
                    for task in next_tasks[:3]:  # Show top 3
                        print(f"  - {task.title} ({task.estimated_minutes}min)")
                
            except ValueError as e:
                print(f"❌ {e}")
                sys.exit(1)
            return
        
        # Create work plan
        if not args.goal:
            args.goal = input("Enter goal to plan for: ")
        
        print("📋 Creating comprehensive work plan...")
        print("This will break down your goal into manageable, testable chunks.\n")
        
        work_plan = planner.create_work_plan(args.goal, args.prd, args.complexity)
        
        print(f"\n📋 Work Plan: {work_plan.name}")
        print(f"🎯 Goal: {work_plan.goal}")
        print(f"📊 Total Time: {work_plan.total_estimated_hours:.1f} hours")
        print(f"📝 Tasks: {len(work_plan.tasks)}")
        
        if args.prd:
            print(f"📄 PRD: {args.prd}")
        
        # Show timeline estimation
        timeline = planner.estimate_timeline(work_plan)
        print(f"\n⏱️ Timeline Estimates:")
        print(f"  Sequential: {timeline['sequential_hours']:.1f} hours")
        print(f"  With parallel work: {timeline['parallel_estimate']:.1f} hours")
        
        if timeline['milestones']:
            print(f"\n🎯 Key Milestones:")
            for milestone in timeline['milestones']:
                print(f"  - {milestone['name']} ({milestone['cumulative_hours']:.1f}h)")
        
        print(f"\n✅ Work plan saved. Use 'claude plan-work --progress={work_plan.name}' to track progress.")
        
    except ImportError as e:
        print(f"❌ Error: Could not import work-planner: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error planning work: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()