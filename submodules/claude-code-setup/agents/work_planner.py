"""
Work Planner Agent

Breaks down complex features into small, manageable, testable chunks.
Critical for maintaining productivity and avoiding overwhelming tasks.

Key responsibilities:
- Smart task segmentation (15-30 minute chunks)
- Dependency analysis and sequencing
- Risk assessment and mitigation planning
- Time estimation and progress tracking
- Integration with PRD requirements
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"

@dataclass
class WorkTask:
    """Represents a single work task."""
    id: str
    title: str
    description: str
    estimated_minutes: int
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = None
    acceptance_criteria: List[str] = None
    risks: List[str] = None
    tags: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.risks is None:
            self.risks = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass 
class WorkPlan:
    """Represents a complete work plan."""
    name: str
    goal: str
    tasks: List[WorkTask]
    total_estimated_hours: float
    created_at: datetime
    prd_reference: Optional[str] = None

class WorkPlanner:
    """Agent for intelligent work planning and task breakdown."""
    
    def __init__(self, project_root: str = None):
        """Initialize work planner."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.memory_bank_path = self.project_root / "memory-bank"
        self.work_plans = {}
        
    def create_work_plan(self, 
                        goal: str,
                        prd_name: str = None,
                        complexity: str = "medium") -> WorkPlan:
        """
        Create a comprehensive work plan for a goal.
        
        Args:
            goal: High-level goal to accomplish
            prd_name: Associated PRD name if available
            complexity: Expected complexity (low/medium/high)
        
        Returns:
            Complete work plan with segmented tasks
        """
        print("📋 Work Planner - Creating Comprehensive Plan")
        print("=" * 50)
        print(f"Goal: {goal}")
        print(f"Complexity: {complexity}")
        if prd_name:
            print(f"PRD Reference: {prd_name}")
        print()
        
        # Analyze the goal and create initial breakdown
        initial_breakdown = self._analyze_goal(goal, complexity)
        
        # Get additional context
        project_context = self._get_project_context()
        prd_context = self._get_prd_context(prd_name) if prd_name else None
        
        # Interactive refinement
        tasks = self._interactive_task_breakdown(initial_breakdown, project_context, prd_context)
        
        # Analyze dependencies
        self._analyze_dependencies(tasks)
        
        # Risk assessment
        self._assess_risks(tasks)
        
        # Time estimation validation
        self._validate_time_estimates(tasks)
        
        # Create work plan
        work_plan = WorkPlan(
            name=self._generate_plan_name(goal),
            goal=goal,
            tasks=tasks,
            total_estimated_hours=sum(task.estimated_minutes for task in tasks) / 60,
            created_at=datetime.now(),
            prd_reference=prd_name
        )
        
        # Save work plan
        self._save_work_plan(work_plan)
        
        print(f"\n✅ Work plan created with {len(tasks)} tasks")
        print(f"📊 Total estimated time: {work_plan.total_estimated_hours:.1f} hours")
        print("\n📋 Task Breakdown:")
        self._display_task_summary(tasks)
        
        return work_plan
    
    def break_down_task(self, task_description: str, max_minutes: int = 30) -> List[WorkTask]:
        """
        Break down a single task into smaller subtasks.
        
        Args:
            task_description: Description of task to break down
            max_minutes: Maximum minutes per subtask
        
        Returns:
            List of smaller work tasks
        """
        print(f"🔨 Breaking down task: {task_description}")
        print(f"Target: Subtasks ≤ {max_minutes} minutes each")
        print()
        
        # Analyze task complexity
        complexity = self._estimate_task_complexity(task_description)
        
        if complexity <= max_minutes:
            print("✅ Task is already appropriately sized")
            return [WorkTask(
                id=self._generate_task_id(),
                title=task_description,
                description=task_description,
                estimated_minutes=complexity,
                priority=TaskPriority.MEDIUM
            )]
        
        # Interactive breakdown
        print(f"Task estimated at {complexity} minutes - needs breakdown")
        subtasks = self._interactive_subtask_breakdown(task_description, max_minutes)
        
        return subtasks
    
    def analyze_dependencies(self, tasks: List[WorkTask]) -> Dict[str, List[str]]:
        """
        Analyze task dependencies and create dependency graph.
        
        Args:
            tasks: List of tasks to analyze
        
        Returns:
            Dependency mapping
        """
        dependency_graph = {}
        
        print("🔗 Dependency Analysis")
        print("-" * 30)
        
        for task in tasks:
            print(f"\nTask: {task.title}")
            print(f"Current dependencies: {task.dependencies}")
            
            # Ask about dependencies with other tasks
            potential_deps = [t.id for t in tasks if t.id != task.id]
            if potential_deps:
                print("Does this task depend on any other tasks?")
                for i, other_task in enumerate([t for t in tasks if t.id != task.id], 1):
                    print(f"  {i}. {other_task.title}")
                
                response = input("Enter task numbers (comma-separated, or 'none'): ").strip()
                if response.lower() != 'none':
                    try:
                        indices = [int(x.strip()) - 1 for x in response.split(',')]
                        other_tasks = [t for t in tasks if t.id != task.id]
                        for idx in indices:
                            if 0 <= idx < len(other_tasks):
                                task.dependencies.append(other_tasks[idx].id)
                    except ValueError:
                        pass
            
            dependency_graph[task.id] = task.dependencies
        
        # Validate no circular dependencies
        self._validate_dependencies(dependency_graph)
        
        return dependency_graph
    
    def estimate_timeline(self, work_plan: WorkPlan) -> Dict[str, Any]:
        """
        Create timeline estimation for work plan.
        
        Args:
            work_plan: Work plan to analyze
        
        Returns:
            Timeline analysis with milestones
        """
        # Sort tasks by dependencies
        sorted_tasks = self._topological_sort(work_plan.tasks)
        
        # Calculate timeline
        timeline = {
            "sequential_hours": sum(task.estimated_minutes for task in sorted_tasks) / 60,
            "parallel_estimate": self._calculate_parallel_timeline(sorted_tasks),
            "milestones": self._identify_milestones(sorted_tasks),
            "critical_path": self._find_critical_path(sorted_tasks)
        }
        
        return timeline
    
    def track_progress(self, plan_name: str) -> Dict[str, Any]:
        """
        Track progress on a work plan.
        
        Args:
            plan_name: Name of work plan to track
        
        Returns:
            Progress analysis
        """
        if plan_name not in self.work_plans:
            raise ValueError(f"Work plan not found: {plan_name}")
        
        work_plan = self.work_plans[plan_name]
        
        # Calculate progress metrics
        total_tasks = len(work_plan.tasks)
        completed_tasks = len([t for t in work_plan.tasks if t.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([t for t in work_plan.tasks if t.status == TaskStatus.IN_PROGRESS])
        blocked_tasks = len([t for t in work_plan.tasks if t.status == TaskStatus.BLOCKED])
        
        completed_minutes = sum(t.estimated_minutes for t in work_plan.tasks if t.status == TaskStatus.COMPLETED)
        total_minutes = sum(t.estimated_minutes for t in work_plan.tasks)
        
        return {
            "plan_name": plan_name,
            "completion_percentage": (completed_minutes / total_minutes) * 100 if total_minutes > 0 else 0,
            "tasks_completed": completed_tasks,
            "tasks_total": total_tasks,
            "tasks_in_progress": in_progress_tasks,
            "tasks_blocked": blocked_tasks,
            "hours_completed": completed_minutes / 60,
            "hours_total": total_minutes / 60,
            "next_available_tasks": self._get_next_available_tasks(work_plan)
        }
    
    def _analyze_goal(self, goal: str, complexity: str) -> List[str]:
        """Analyze goal and create initial task breakdown."""
        # Pattern-based analysis
        if "api" in goal.lower():
            return self._api_breakdown_pattern(goal)
        elif any(word in goal.lower() for word in ["ui", "interface", "frontend", "gui"]):
            return self._ui_breakdown_pattern(goal)
        elif any(word in goal.lower() for word in ["test", "testing", "coverage"]):
            return self._testing_breakdown_pattern(goal)
        elif any(word in goal.lower() for word in ["refactor", "optimize", "improve"]):
            return self._refactoring_breakdown_pattern(goal)
        else:
            return self._generic_breakdown_pattern(goal, complexity)
    
    def _api_breakdown_pattern(self, goal: str) -> List[str]:
        """Pattern for API-related goals."""
        return [
            "Design API endpoints and data models",
            "Implement request/response validation",
            "Create API route handlers",
            "Add comprehensive error handling",
            "Write API integration tests",
            "Create API documentation",
            "Add authentication/authorization if needed",
            "Performance testing and optimization"
        ]
    
    def _ui_breakdown_pattern(self, goal: str) -> List[str]:
        """Pattern for UI-related goals."""
        return [
            "Design component structure and layout",
            "Create base components and styling",
            "Implement user interaction logic",
            "Add form validation and error handling",
            "Create responsive design adaptations",
            "Add accessibility features",
            "Write component unit tests",
            "Integration testing with user workflows"
        ]
    
    def _testing_breakdown_pattern(self, goal: str) -> List[str]:
        """Pattern for testing-related goals."""
        return [
            "Analyze current test coverage gaps",
            "Design test strategy and structure",
            "Write unit tests for core functionality",
            "Create integration tests",
            "Add edge case and error condition tests",
            "Set up test fixtures and mock data",
            "Create performance/load tests if needed",
            "Configure continuous testing pipeline"
        ]
    
    def _refactoring_breakdown_pattern(self, goal: str) -> List[str]:
        """Pattern for refactoring-related goals."""
        return [
            "Analyze current code structure and identify issues",
            "Create comprehensive test coverage for existing code",
            "Design improved architecture/structure",
            "Refactor in small, safe increments",
            "Update related documentation",
            "Performance benchmarking before/after",
            "Update any affected APIs or interfaces",
            "Validation testing to ensure no regressions"
        ]
    
    def _generic_breakdown_pattern(self, goal: str, complexity: str) -> List[str]:
        """Generic pattern for any goal."""
        base_tasks = [
            "Research and understand requirements",
            "Design approach and architecture",
            "Implement core functionality", 
            "Add error handling and edge cases",
            "Create comprehensive tests",
            "Write documentation",
            "Integration and validation testing"
        ]
        
        if complexity == "high":
            base_tasks.extend([
                "Performance optimization",
                "Security analysis",
                "Deployment considerations"
            ])
        
        return base_tasks
    
    def _interactive_task_breakdown(self, initial_breakdown: List[str], 
                                  project_context: str, 
                                  prd_context: str) -> List[WorkTask]:
        """Interactively refine the task breakdown."""
        print("📝 Task Breakdown Refinement")
        print("-" * 30)
        print("Here's the initial breakdown based on your goal:")
        
        for i, task in enumerate(initial_breakdown, 1):
            print(f"  {i}. {task}")
        
        print("\nLet's refine each task to be specific and time-boxed:")
        
        tasks = []
        for i, initial_task in enumerate(initial_breakdown):
            print(f"\n--- Task {i+1}: {initial_task} ---")
            
            # Refine task description
            refined_title = input(f"Refined title (or press Enter to keep): ").strip()
            if not refined_title:
                refined_title = initial_task
            
            # Get detailed description
            description = input("Detailed description: ").strip()
            if not description:
                description = refined_title
            
            # Time estimation
            while True:
                try:
                    estimated_minutes = int(input("Estimated minutes (15-45 recommended): "))
                    if estimated_minutes > 60:
                        print("⚠️ Task might be too large. Consider breaking it down further.")
                        break_down = input("Break down into smaller tasks? (y/n): ").lower()
                        if break_down.startswith('y'):
                            subtasks = self._break_down_large_task(refined_title, estimated_minutes)
                            tasks.extend(subtasks)
                            continue
                    break
                except ValueError:
                    print("Please enter a valid number of minutes")
            
            # Priority
            priority_options = ["critical", "high", "medium", "low"]
            print("Priority options: critical, high, medium, low")
            priority_input = input("Priority [medium]: ").strip().lower()
            if priority_input not in priority_options:
                priority_input = "medium"
            priority = TaskPriority(priority_input)
            
            # Acceptance criteria
            print("Acceptance criteria (empty line to finish):")
            acceptance_criteria = []
            while True:
                criterion = input(f"  Criterion #{len(acceptance_criteria)+1}: ").strip()
                if not criterion:
                    break
                acceptance_criteria.append(criterion)
            
            # Create task
            task = WorkTask(
                id=self._generate_task_id(),
                title=refined_title,
                description=description,
                estimated_minutes=estimated_minutes,
                priority=priority,
                acceptance_criteria=acceptance_criteria,
                tags=self._extract_tags(description)
            )
            
            tasks.append(task)
        
        # Ask if any additional tasks are needed
        print("\nAny additional tasks needed?")
        while True:
            additional = input("Additional task (or 'done'): ").strip()
            if additional.lower() == 'done' or not additional:
                break
            
            # Quick task creation
            estimated_minutes = int(input("Estimated minutes: ") or "30")
            task = WorkTask(
                id=self._generate_task_id(),
                title=additional,
                description=additional,
                estimated_minutes=estimated_minutes,
                priority=TaskPriority.MEDIUM
            )
            tasks.append(task)
        
        return tasks
    
    def _break_down_large_task(self, title: str, minutes: int) -> List[WorkTask]:
        """Break down a task that's too large."""
        print(f"Breaking down: {title} ({minutes} minutes)")
        
        subtasks = []
        remaining_minutes = minutes
        subtask_count = 1
        
        while remaining_minutes > 45:
            print(f"\nSubtask {subtask_count}:")
            subtask_title = input("Subtask title: ").strip()
            subtask_minutes = int(input("Estimated minutes: ") or "30")
            
            subtask = WorkTask(
                id=self._generate_task_id(),
                title=f"{title} - {subtask_title}",
                description=subtask_title,
                estimated_minutes=subtask_minutes,
                priority=TaskPriority.MEDIUM
            )
            
            subtasks.append(subtask)
            remaining_minutes -= subtask_minutes
            subtask_count += 1
            
            if remaining_minutes <= 45:
                # Create final subtask with remaining time
                final_title = input(f"Final subtask ({remaining_minutes} min): ").strip()
                if final_title:
                    final_task = WorkTask(
                        id=self._generate_task_id(),
                        title=f"{title} - {final_title}",
                        description=final_title,
                        estimated_minutes=remaining_minutes,
                        priority=TaskPriority.MEDIUM
                    )
                    subtasks.append(final_task)
                break
        
        return subtasks
    
    def _analyze_dependencies(self, tasks: List[WorkTask]):
        """Analyze and set task dependencies."""
        print("\n🔗 Dependency Analysis")
        print("Let's identify task dependencies to create the optimal sequence.")
        
        for i, task in enumerate(tasks):
            if i == 0:
                continue  # First task typically has no dependencies
            
            print(f"\nTask: {task.title}")
            print("Previous tasks:")
            for j, prev_task in enumerate(tasks[:i], 1):
                print(f"  {j}. {prev_task.title}")
            
            deps_input = input("Dependencies (enter numbers, comma-separated, or 'none'): ").strip()
            if deps_input.lower() != 'none':
                try:
                    dep_indices = [int(x.strip()) - 1 for x in deps_input.split(',')]
                    for dep_idx in dep_indices:
                        if 0 <= dep_idx < i:
                            task.dependencies.append(tasks[dep_idx].id)
                except ValueError:
                    pass
    
    def _assess_risks(self, tasks: List[WorkTask]):
        """Assess risks for each task."""
        print("\n⚠️ Risk Assessment")
        print("Let's identify potential risks and blockers.")
        
        for task in tasks:
            print(f"\nTask: {task.title}")
            print("Potential risks (empty line to finish):")
            
            while True:
                risk = input(f"  Risk #{len(task.risks)+1}: ").strip()
                if not risk:
                    break
                task.risks.append(risk)
    
    def _validate_time_estimates(self, tasks: List[WorkTask]):
        """Validate and adjust time estimates."""
        print("\n⏱️ Time Estimate Validation")
        
        large_tasks = [t for t in tasks if t.estimated_minutes > 45]
        if large_tasks:
            print("These tasks might be too large:")
            for task in large_tasks:
                print(f"  - {task.title}: {task.estimated_minutes} minutes")
            
            adjust = input("Would you like to adjust any estimates? (y/n): ").lower()
            if adjust.startswith('y'):
                for task in large_tasks:
                    new_estimate = input(f"New estimate for '{task.title}' [{task.estimated_minutes}]: ").strip()
                    if new_estimate.isdigit():
                        task.estimated_minutes = int(new_estimate)
        
        # Check for unrealistically small tasks
        small_tasks = [t for t in tasks if t.estimated_minutes < 10]
        if small_tasks:
            print("These tasks might be too small (consider combining):")
            for task in small_tasks:
                print(f"  - {task.title}: {task.estimated_minutes} minutes")
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.work_plans)}"
    
    def _generate_plan_name(self, goal: str) -> str:
        """Generate work plan name from goal."""
        name = goal.lower().replace(' ', '_')[:30]
        return f"{name}_{datetime.now().strftime('%Y%m%d')}"
    
    def _extract_tags(self, description: str) -> List[str]:
        """Extract relevant tags from task description."""
        tags = []
        keywords = {
            'api': ['api', 'endpoint', 'route', 'service'],
            'frontend': ['ui', 'interface', 'component', 'styling'],
            'backend': ['server', 'database', 'logic', 'processing'],
            'testing': ['test', 'spec', 'coverage', 'validation'],
            'documentation': ['docs', 'readme', 'documentation', 'guide']
        }
        
        desc_lower = description.lower()
        for tag, words in keywords.items():
            if any(word in desc_lower for word in words):
                tags.append(tag)
        
        return tags
    
    def _get_project_context(self) -> str:
        """Get project context from memory bank."""
        try:
            if self.memory_bank_path.exists():
                active_context_path = self.memory_bank_path / "activeContext.md"
                if active_context_path.exists():
                    with open(active_context_path, 'r') as f:
                        return f.read()[:500]  # Truncate for relevance
        except Exception:
            pass
        
        return f"Project root: {self.project_root}"
    
    def _get_prd_context(self, prd_name: str) -> Optional[str]:
        """Get PRD context if available."""
        try:
            prd_path = self.memory_bank_path / "prds" / f"{prd_name}.md"
            if prd_path.exists():
                with open(prd_path, 'r') as f:
                    content = f.read()
                    # Extract goal and requirements sections
                    lines = content.split('\n')
                    relevant_lines = []
                    in_relevant_section = False
                    
                    for line in lines:
                        if any(section in line for section in ['## Goal', '## Requirements', '## Success']):
                            in_relevant_section = True
                            relevant_lines.append(line)
                        elif line.startswith('## ') and in_relevant_section:
                            in_relevant_section = False
                        elif in_relevant_section:
                            relevant_lines.append(line)
                    
                    return '\n'.join(relevant_lines[:20])  # Keep it focused
        except Exception:
            pass
        
        return None
    
    def _save_work_plan(self, work_plan: WorkPlan):
        """Save work plan to memory bank."""
        self.work_plans[work_plan.name] = work_plan
        
        # Also save to file for persistence
        work_plans_dir = self.memory_bank_path / "work-plans"
        work_plans_dir.mkdir(exist_ok=True)
        
        plan_file = work_plans_dir / f"{work_plan.name}.json"
        plan_data = {
            "name": work_plan.name,
            "goal": work_plan.goal,
            "total_estimated_hours": work_plan.total_estimated_hours,
            "created_at": work_plan.created_at.isoformat(),
            "prd_reference": work_plan.prd_reference,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "estimated_minutes": task.estimated_minutes,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "dependencies": task.dependencies,
                    "acceptance_criteria": task.acceptance_criteria,
                    "risks": task.risks,
                    "tags": task.tags,
                    "created_at": task.created_at.isoformat()
                } for task in work_plan.tasks
            ]
        }
        
        import json
        with open(plan_file, 'w') as f:
            json.dump(plan_data, f, indent=2)
    
    def _display_task_summary(self, tasks: List[WorkTask]):
        """Display summary of tasks."""
        for i, task in enumerate(tasks, 1):
            priority_emoji = {
                TaskPriority.CRITICAL: "🔴",
                TaskPriority.HIGH: "🟠", 
                TaskPriority.MEDIUM: "🟡",
                TaskPriority.LOW: "🟢"
            }
            
            deps_str = f" (depends: {len(task.dependencies)})" if task.dependencies else ""
            risks_str = f" ⚠️{len(task.risks)}" if task.risks else ""
            
            print(f"  {i}. {priority_emoji[task.priority]} {task.title} ({task.estimated_minutes}min){deps_str}{risks_str}")
    
    def _estimate_task_complexity(self, task_description: str) -> int:
        """Estimate task complexity in minutes."""
        # Simple heuristic based on keywords and description length
        base_time = 20
        
        complexity_keywords = {
            'high': ['complex', 'integrate', 'refactor', 'architecture', 'security', 'performance'],
            'medium': ['implement', 'create', 'build', 'design', 'configure'],
            'low': ['update', 'fix', 'adjust', 'modify', 'change']
        }
        
        desc_lower = task_description.lower()
        
        for level, keywords in complexity_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                if level == 'high':
                    base_time *= 2.5
                elif level == 'medium':
                    base_time *= 1.5
                break
        
        # Adjust for description length
        if len(task_description) > 100:
            base_time *= 1.3
        
        return int(base_time)
    
    def _interactive_subtask_breakdown(self, task_description: str, max_minutes: int) -> List[WorkTask]:
        """Interactive breakdown of large task into subtasks."""
        print(f"Breaking down: {task_description}")
        print("Enter subtasks (empty line to finish):")
        
        subtasks = []
        while True:
            subtask_title = input(f"Subtask #{len(subtasks)+1}: ").strip()
            if not subtask_title:
                break
            
            estimated_minutes = int(input("Estimated minutes: ") or str(max_minutes))
            
            subtask = WorkTask(
                id=self._generate_task_id(),
                title=subtask_title,
                description=subtask_title,
                estimated_minutes=min(estimated_minutes, max_minutes),
                priority=TaskPriority.MEDIUM
            )
            
            subtasks.append(subtask)
        
        return subtasks
    
    def _validate_dependencies(self, dependency_graph: Dict[str, List[str]]):
        """Validate dependency graph for circular dependencies."""
        # Simple cycle detection
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependency_graph:
            if node not in visited:
                if has_cycle(node):
                    print("⚠️ Circular dependency detected! Please review dependencies.")
                    return False
        
        return True
    
    def _topological_sort(self, tasks: List[WorkTask]) -> List[WorkTask]:
        """Sort tasks based on dependencies."""
        # Build graph
        task_map = {task.id: task for task in tasks}
        
        # Kahn's algorithm for topological sorting
        in_degree = {task.id: 0 for task in tasks}
        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1
        
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(task_map[current])
            
            # Update in-degrees
            for task in tasks:
                if current in task.dependencies:
                    in_degree[task.id] -= 1
                    if in_degree[task.id] == 0:
                        queue.append(task.id)
        
        return result
    
    def _calculate_parallel_timeline(self, sorted_tasks: List[WorkTask]) -> float:
        """Calculate timeline assuming some parallel work."""
        # Simplified parallel calculation
        total_sequential = sum(task.estimated_minutes for task in sorted_tasks) / 60
        return total_sequential * 0.7  # Assume 30% parallelization
    
    def _identify_milestones(self, tasks: List[WorkTask]) -> List[Dict[str, Any]]:
        """Identify key milestones in the task list."""
        milestones = []
        cumulative_hours = 0
        
        for i, task in enumerate(tasks):
            cumulative_hours += task.estimated_minutes / 60
            
            # Create milestone every ~4 hours or for critical tasks
            if cumulative_hours >= 4 or task.priority == TaskPriority.CRITICAL:
                milestones.append({
                    "name": f"Milestone {len(milestones)+1}: {task.title}",
                    "task_count": i + 1,
                    "cumulative_hours": cumulative_hours
                })
                cumulative_hours = 0  # Reset for next milestone
        
        return milestones
    
    def _find_critical_path(self, tasks: List[WorkTask]) -> List[str]:
        """Find critical path through tasks."""
        # Simplified critical path - just the longest dependency chain
        max_chain = []
        
        def find_longest_chain(task_id, current_chain):
            nonlocal max_chain
            task = next((t for t in tasks if t.id == task_id), None)
            if not task:
                return
            
            current_chain.append(task_id)
            
            if not task.dependencies:
                if len(current_chain) > len(max_chain):
                    max_chain = current_chain.copy()
            else:
                for dep in task.dependencies:
                    find_longest_chain(dep, current_chain.copy())
        
        for task in tasks:
            if not task.dependencies:  # Start from tasks with no dependencies
                find_longest_chain(task.id, [])
        
        return max_chain
    
    def _get_next_available_tasks(self, work_plan: WorkPlan) -> List[WorkTask]:
        """Get tasks that can be started now (dependencies satisfied)."""
        completed_task_ids = {t.id for t in work_plan.tasks if t.status == TaskStatus.COMPLETED}
        
        available_tasks = []
        for task in work_plan.tasks:
            if task.status == TaskStatus.PENDING:
                if all(dep in completed_task_ids for dep in task.dependencies):
                    available_tasks.append(task)
        
        return sorted(available_tasks, key=lambda t: t.priority.value, reverse=True)


def main():
    """Command line interface for work planner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Work Planner Agent")
    parser.add_argument("action", choices=["plan", "breakdown", "progress", "timeline"])
    parser.add_argument("--goal", help="Goal to plan for")
    parser.add_argument("--task", help="Task to break down")
    parser.add_argument("--plan", help="Plan name for progress/timeline")
    parser.add_argument("--prd", help="Associated PRD name")
    parser.add_argument("--complexity", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    planner = WorkPlanner(args.project_root)
    
    if args.action == "plan":
        if not args.goal:
            args.goal = input("Enter goal to plan for: ")
        work_plan = planner.create_work_plan(args.goal, args.prd, args.complexity)
        print(f"\nWork plan created: {work_plan.name}")
    
    elif args.action == "breakdown":
        if not args.task:
            args.task = input("Enter task to break down: ")
        subtasks = planner.break_down_task(args.task)
        print(f"\nBroke down into {len(subtasks)} subtasks:")
        for i, subtask in enumerate(subtasks, 1):
            print(f"  {i}. {subtask.title} ({subtask.estimated_minutes}min)")
    
    elif args.action == "progress":
        if not args.plan:
            args.plan = input("Enter plan name: ")
        try:
            progress = planner.track_progress(args.plan)
            print(f"\nProgress for {args.plan}:")
            print(f"  Completion: {progress['completion_percentage']:.1f}%")
            print(f"  Tasks: {progress['tasks_completed']}/{progress['tasks_total']}")
            print(f"  Time: {progress['hours_completed']:.1f}/{progress['hours_total']:.1f} hours")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()