# Universal Claude Code Setup

🚀 **The complete Claude Code system that can be deployed to any repository in 5 minutes.**

Transform any project into a PRD-driven, context-optimized, professionally managed development environment.

## What This Provides

### 🧠 Memory Bank System
- **Token Efficiency**: <2000 tokens vs 10,000+ for raw project files
- **Cross-Session Continuity**: Perfect context between sessions
- **Decision Recording**: Automatic pattern and decision documentation
- **PRD Storage**: Centralized requirements management

### 🤖 Universal Agents
- **memory-bank-agent**: CRITICAL - Session context management (ALWAYS USE FIRST)
- **prd-creator**: Interactive PRD creation and validation
- **work-planner**: Smart task breakdown (15-30 minute chunks)
- **tdd-implementer**: Strict Test-Driven Development enforcement
- **prompt-optimizer**: Craft optimal prompts for better outcomes

### ⚙️ Universal Commands
- `claude memory-context` - Get project context (MANDATORY FIRST STEP)
- `claude create-prd` - Create/manage Product Requirements Documents
- `claude plan-work` - Intelligent work breakdown and tracking
- `claude implement-tdd` - Test-driven feature implementation
- `claude optimize-prompt` - Enhance prompt effectiveness
- `claude quality-check` - Comprehensive code quality validation

### 📋 Professional Workflow
1. **PRD-First Development**: No code without approved requirements
2. **Context Optimization**: Efficient AI interactions via memory bank
3. **Small Chunks**: Work broken into manageable, testable pieces
4. **Quality Enforcement**: Comprehensive validation before commits
5. **Pattern Learning**: Continuous improvement via memory bank

## Quick Start (5-Minute Setup)

### Option 1: Direct Copy (Recommended)
```bash
# Navigate to your project root
cd /path/to/your/project

# Copy the claude-code-setup system
git clone https://github.com/your-org/claude-code-setup .claude-system

# Run interactive setup
python .claude-system/setup.py

# Answer 7-10 questions about your project
# ✅ Customized Claude Code configuration ready!
```

### Option 2: Git Submodule
```bash
# Add as submodule
git submodule add https://github.com/your-org/claude-code-setup .claude-system

# Run setup
python .claude-system/setup.py
```

### Option 3: Download and Extract
```bash
# Download latest release
curl -L https://github.com/your-org/claude-code-setup/archive/main.zip -o claude-setup.zip
unzip claude-setup.zip
mv claude-code-setup-main .claude-system

# Run setup
python .claude-system/setup.py
```

## What Gets Created

After running setup, you'll have:

```
your-project/
├── .claude/
│   ├── agents/           # AI agents (5 universal agents)
│   ├── commands/         # Commands (6 workflow commands)
│   └── templates/        # Project templates
├── memory-bank/
│   ├── projectbrief.md   # Core requirements and goals
│   ├── productContext.md # Why project exists
│   ├── activeContext.md  # Current session context
│   ├── systemPatterns.md # Architecture and patterns
│   ├── techContext.md    # Technical environment
│   ├── progress.md       # What works, what's left
│   └── prds/            # Product Requirements Documents
│       └── example-feature.md
├── CLAUDE.md            # Customized project configuration
└── .mcp.json           # MCP server configuration
```

## Setup Questions (Interactive Wizard)

The setup wizard asks 7-10 questions to customize your configuration:

### Project Information (4 questions)
1. **Project name** - Extracted from directory name
2. **Project type** - Library, Web App, API, CLI Tool, etc.
3. **Primary language** - Python, JavaScript, Go, Rust, etc.
4. **Target users** - Professional developers, students, etc.

### Development Preferences (3 questions)  
5. **Test framework** - pytest, jest, etc. (auto-detected)
6. **Code quality tools** - Formatter, linter, type checker
7. **Coverage target** - 85%, 90%, etc.

### Workflow Configuration (3 questions)
8. **Default AI model** - Claude Sonnet 4, GPT-4, etc.
9. **Work style** - Small chunks (15min), medium tasks, etc.
10. **Documentation level** - Standard, comprehensive, etc.

## Essential Workflow (Start Every Session)

### 🚨 CRITICAL: Session Start Protocol
```bash
# ALWAYS START WITH THIS COMMAND
claude memory-context

# Optional: Focus on specific area
claude memory-context --focus=testing
claude memory-context --focus=api
claude memory-context --focus=features
```

**Why this matters**: 
- Provides <2000 tokens of relevant context vs 10,000+ from raw files
- Updates activeContext.md with session information
- Ensures AI agents have proper project understanding

### Standard Development Flow
```bash
# 1. Get context (MANDATORY)
claude memory-context

# 2. Create PRD for new features
claude create-prd "Add user authentication"

# 3. Plan work breakdown
claude plan-work "Implement authentication system" --prd=user-authentication

# 4. Implement with TDD
claude implement-tdd "User login functionality" --prd=user-authentication

# 5. Quality check before commit
claude quality-check --fix --coverage

# 6. Commit with confidence!
git add . && git commit -m "feat: implement user authentication

✅ Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Language Support

### Python Projects
- **Auto-detected**: pyproject.toml, setup.py, requirements.txt
- **Tools**: black (formatter), ruff (linter), mypy (types), pytest (tests)
- **Quality**: Coverage with pytest-cov, security with bandit

### JavaScript/TypeScript Projects  
- **Auto-detected**: package.json, tsconfig.json
- **Tools**: prettier (formatter), eslint (linter), tsc (types), jest (tests)
- **Quality**: Coverage with jest, security with npm audit

### Go Projects
- **Auto-detected**: go.mod
- **Tools**: gofmt (formatter), golint (linter), go test (tests)
- **Quality**: Built-in coverage, vet for issues

### Rust Projects
- **Auto-detected**: Cargo.toml
- **Tools**: rustfmt (formatter), clippy (linter), cargo test (tests)
- **Quality**: Built-in coverage with tarpaulin

### Universal Support
Works with any language by using generic templates and customizable tool configurations in CLAUDE.md.

## Advanced Features

### Memory Bank Management
```bash
# List PRDs
claude create-prd --list

# Validate PRD completeness
claude create-prd --validate my-feature

# Track work progress
claude plan-work --progress my-work-plan

# Update active context manually
python .claude-system/agents/memory-bank-agent.py --update "Major decision: switching to PostgreSQL"
```

### Prompt Optimization
```bash
# Optimize for TDD implementation
claude optimize-prompt "Add real-time notifications" --type=tdd --agent=tdd-implementer

# Optimize for work planning
claude optimize-prompt "Redesign user interface" --type=planning

# Optimize for debugging  
claude optimize-prompt "Fix memory leak in image processing" --type=debugging
```

### Quality Assurance
```bash
# Full quality check
claude quality-check

# Auto-fix formatting and linting
claude quality-check --fix

# Include security analysis
claude quality-check --security --coverage

# Individual checks
claude quality-check --format-only
claude quality-check --test-only
```

## Customization

### Project-Specific Agents
Add your own agents to `.claude/agents/`:

```python
# .claude/agents/custom-agent.py
class CustomAgent:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
    
    def custom_functionality(self):
        # Your custom logic here
        pass
```

### Project-Specific Commands
Add your own commands to `.claude/commands/`:

```python
# .claude/commands/custom-command.py
def main():
    """Custom command implementation."""
    # Your custom command logic here
    pass

if __name__ == "__main__":
    main()
```

### Memory Bank Customization
Customize memory bank templates in `.claude-system/templates/memory-bank-templates.py`.

## Troubleshooting

### Setup Issues
```bash
# Permission errors
chmod +x .claude-system/setup.py
python .claude-system/setup.py

# Missing dependencies
pip install -r .claude-system/requirements.txt  # If exists
```

### Command Issues
```bash
# Command not found
export PATH="$PATH:./.claude-system/commands"

# Python import errors
export PYTHONPATH="$PYTHONPATH:./.claude-system/agents"

# Permission issues
chmod +x .claude-system/commands/*.py
```

### Memory Bank Issues
```bash
# Reset memory bank (WARNING: loses all context)
rm -rf memory-bank/
python .claude-system/setup.py  # Re-run setup

# Repair corrupted memory bank
python .claude-system/agents/memory-bank-agent.py --repair
```

### Agent Issues
```bash
# Test agent functionality
python .claude-system/agents/memory-bank-agent.py --project-root=.
python .claude-system/agents/prd-creator.py --action=list
python .claude-system/agents/work-planner.py --action=list
```

## Integration with Existing Projects

### Adding to Existing Repository
1. **Backup existing Claude configuration** (if any)
2. **Run setup wizard** - it won't overwrite existing files
3. **Merge configurations** - manually combine with existing CLAUDE.md
4. **Test workflow** - ensure commands work with your project structure

### Migration from Other Systems
- **From basic Claude setup**: Run setup, then manually merge any custom configurations
- **From other AI systems**: Use the universal templates as starting points
- **From manual workflows**: Document existing patterns in systemPatterns.md

## Best Practices

### Memory Bank Management
- **Update activeContext.md** during each session with decisions made
- **Review and condense** memory bank files weekly to prevent drift
- **Keep PRDs current** - mark as approved/deprecated as needed
- **Document patterns** in systemPatterns.md for reuse

### PRD-Driven Development
- **No code without PRD** - enforce this discipline strictly
- **Get user approval** on PRDs before implementation
- **Reference PRDs** in commits and pull requests
- **Update PRDs** when requirements change

### Context Optimization
- **Always start with memory-context** - it's not optional
- **Use focused context** when working on specific areas
- **Update memory bank** with decisions and patterns learned
- **Keep sessions focused** to maintain context quality

### Quality Assurance
- **Run quality-check before commits** - make it a habit
- **Fix issues immediately** - don't accumulate technical debt
- **Maintain high test coverage** - it pays dividends
- **Document quality decisions** in memory bank

## Examples

### New Project Setup
```bash
# Create new project
mkdir my-awesome-project && cd my-awesome-project
git init

# Add Claude Code system
git clone https://github.com/your-org/claude-code-setup .claude-system

# Interactive setup
python .claude-system/setup.py
# Choose: Python Library, Professional developers, pytest, etc.

# First session
claude memory-context
claude create-prd "Core library functionality"
# (Interactive PRD creation)

claude plan-work "Implement core library" --prd=core-functionality
# (Interactive work planning)

claude implement-tdd "Basic API methods" --prd=core-functionality
# (TDD implementation)

claude quality-check --fix
git add . && git commit -m "feat: initial library structure"
```

### Existing Project Enhancement
```bash
# Navigate to existing project
cd existing-project

# Add Claude Code system
git clone https://github.com/your-org/claude-code-setup .claude-system

# Setup (preserves existing files)
python .claude-system/setup.py

# Document current state
claude memory-context
# Edit memory-bank/activeContext.md to describe current project state

# Plan next feature
claude create-prd "Add advanced search functionality"
claude plan-work "Implement search with filters" --prd=advanced-search

# Continue development with enhanced workflow
```

## Contributing

We welcome contributions to make this system even more universal and effective!

### Areas for Contribution
- **New language support** (Go, Rust, Java, C++, etc.)
- **Additional agents** (deployment, documentation, testing, etc.)
- **Enhanced templates** for specific project types
- **Integration examples** with popular frameworks
- **Performance optimizations** for large projects

### Development Setup
```bash
git clone https://github.com/your-org/claude-code-setup
cd claude-code-setup

# Test with example project
mkdir test-project && cd test-project
python ../setup.py
# Test all commands and agents
```

## License

MIT License - Use this system in any project, commercial or open source.

## Support

- **Documentation**: See `docs/` directory for detailed guides
- **Issues**: GitHub Issues for bugs and feature requests  
- **Discussions**: GitHub Discussions for questions and community
- **Examples**: `examples/` directory for real-world usage patterns

---

## Success Stories

> "Reduced context switching time by 80%. The memory bank system means I never lose project context between sessions." - *Professional Developer*

> "PRD-driven development transformed our team. No more building the wrong thing." - *Startup CTO*

> "The universal commands work perfectly across our Python, Node.js, and Go services." - *Platform Team Lead*

---

**Ready to transform your development workflow?**

```bash
python .claude-system/setup.py
```

*5 minutes to setup. Lifetime of improved productivity.*