from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI
from qa_agent.workspace import get_path, WORKSPACE_ROOT
from qa_agent.playwright_mcp import get_tools as get_playwright_tools


def get_planner_prompt():
    plans_dir = get_path("plans")
    return f"""You are an Expert QA Test Planner Agent.

Your mission is to explore a web application and create test scenarios based on the USER'S REQUEST.

═══════════════════════════════════════════════════════════════════════════════
IMPORTANT: FOLLOW THE USER'S REQUEST
═══════════════════════════════════════════════════════════════════════════════

The user may ask for:
- SPECIFIC features to test (e.g., "test the login form", "test navigation")
- FULL exploration (e.g., "test everything", "explore the whole site")
- TARGETED areas (e.g., "test all forms", "test the footer links")

ADAPT your exploration and test creation to match what the user asked for.
Do NOT test everything if the user only asked for specific features.

═══════════════════════════════════════════════════════════════════════════════
EXPLORATION PROCESS
═══════════════════════════════════════════════════════════════════════════════

1. NAVIGATE to the target URL
2. Take a SNAPSHOT to understand the page structure
3. Based on user request, explore RELEVANT areas:
   - If specific feature requested: focus only on that feature
   - If full test requested: explore all pages and features
4. Identify testable scenarios for the requested scope

═══════════════════════════════════════════════════════════════════════════════
CREATE TEST FILES
═══════════════════════════════════════════════════════════════════════════════

For EACH test scenario, create a markdown file:

```markdown
# Test: [Descriptive Test Name]

## Objective
[What this test verifies]

## Preconditions
- [Any setup required]

## Test Steps
1. Navigate to [URL]
2. [Action]: [Element description]
...

## Expected Results
- [What should happen]

## Element Selectors
- [Element]: [How to locate it]
```

═══════════════════════════════════════════════════════════════════════════════
HOW TO SAVE FILES
═══════════════════════════════════════════════════════════════════════════════

Use write_file tool to save each test scenario:
- Path: {plans_dir}/<test_name>.md
- Example: write_file(path="{plans_dir}/login_test.md", content="...")

WORKSPACE ROOT: {WORKSPACE_ROOT}
PLANS DIRECTORY: {plans_dir}

REQUIREMENTS:
- Create tests ONLY for what the user requested
- Use write_file for EACH test scenario
- Use FULL PATHS
- Call browser_close when done
"""


def create_planner_agent():
    model = ChatOpenAI(model="gpt-4o")
    tools = get_playwright_tools()
    backend = FilesystemBackend(root_dir=str(WORKSPACE_ROOT))
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=get_planner_prompt(),
        backend=backend,
    )
