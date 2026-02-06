# Zero-Touch QA: AI-Powered Autonomous Testing

An intelligent, autonomous QA testing system that uses AI agents to automatically explore web applications, generate test scenarios, execute tests, capture evidence, and post formatted reports to Wrike—all with minimal human intervention.

Built with LangGraph, LangChain DeepAgents, OpenAI GPT-4o, and Playwright.

---

## 🚀 Overview

Zero-Touch QA automates the entire QA workflow:
1. **🔍 AI Planner Agent** - Explores your web application and creates comprehensive test scenarios
2. **▶️ AI Runner Agent** - Executes tests, captures screenshots, and generates detailed reports
3. **📤 Wrike Poster** - Formats and posts QA results to Wrike tasks with audit trail

**Key Innovation:** True autonomous testing with AI-driven test generation and execution—no manual test writing required.

---

## ✨ Key Features

### Autonomous Testing
- **AI-Driven Exploration**: GPT-4o intelligently navigates and understands web applications
- **Automatic Test Generation**: Creates test scenarios based on discovered features
- **Self-Executing Tests**: Runs tests autonomously with Playwright browser automation
- **Visual Evidence**: Captures screenshots at every critical step

### Enterprise Integration
- **Wrike Integration**: Automated posting of formatted QA reports to Wrike tasks
- **Audit Trail**: Saves all reports with timestamps for compliance and tracking
- **Multi-Environment Support**: Configurable for dev/staging/production
- **Build Tracking**: Reports include version, environment, test type, and defect tracking

### Production-Ready Architecture
- **LangGraph Workflow**: Professional multi-agent orchestration with state management
- **Error Handling**: Graceful failure handling and recovery
- **Demo Mode**: Full functionality without requiring API credentials
- **Scalable Design**: Easy to extend with additional integration nodes (Jotform, Slack, etc.)

---

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment variables

Copy the example configuration and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Only for LangGraph Studio
LANGSMITH_API_KEY=your-langsmith-api-key-here

# Optional: Custom test app URL
TEST_APP_URL=http://localhost:5173

# Optional: Custom workspace path
QA_WORKSPACE=/path/to/custom/workspace
```

**Required:**
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys

**Optional:**
- `LANGSMITH_API_KEY`: Only needed for `langgraph dev` - Get from https://smith.langchain.com/settings

## Usage

### Option 1: Manual Workflow Script (Recommended)

Run the complete end-to-end workflow:

```bash
# 1. Start test application (in separate terminal)
cd test_application/react-vet-clinic-dashboard
npm install && npm run dev

# 2. Run the workflow
uv run run_qa_workflow.py
```

This executes: Planner → Runner → Wrike Integration

**Outputs:**
- Test plans: `qa_workspace/plans/`
- Test report: `qa_workspace/reports/test_report.md`
- Screenshots: `qa_workspace/screenshots/`
- Wrike report: `qa_workspace/wrike_reports/`

---

### Option 2: LangGraph Dev Server

For visual workflow monitoring with LangGraph Studio:

```bash
# Requires LANGSMITH_API_KEY in .env

# 1. Start test application (in separate terminal)
cd test_application/react-vet-clinic-dashboard
npm install && npm run dev

# 2. Start LangGraph dev server
uv run langgraph dev

# 3. Open http://localhost:8123 in browser
```

---

### Option 3: Python API

Use programmatically in your own scripts:

```python
from qa_agent.orchestrator import run_full, run_planner, run_runner

# Full workflow with Wrike integration
result = run_full(
    message="Test patient management features",
    post_to_wrike=True,
    wrike_task_id="EXPRESS-2024-001"
)

# Or run individual steps
plan_result = run_planner("Create search functionality tests")
run_result = run_runner()
```

---

## Project Structure

```
Zero-Touch-QA/
├── qa_agent/
│   ├── __init__.py           # Package exports
│   ├── orchestrator.py       # LangGraph workflow (Planner → Runner → Wrike)
│   ├── wrike_integration.py  # Wrike API integration
│   ├── playwright_mcp.py     # Browser automation
│   ├── workspace.py          # Workspace management
│   └── agents/
│       ├── planner.py        # Test scenario generation
│       └── runner.py         # Test execution
├── qa_workspace/
│   ├── plans/                # Generated test scenarios
│   ├── reports/              # Test execution reports
│   ├── screenshots/          # Captured screenshots
│   └── wrike_reports/        # Formatted Wrike reports (audit trail)
├── test_application/         # Sample apps for testing
├── pyproject.toml            # Project configuration
├── .env                      # API keys (create this)
└── README.md                 # This file
```

## 🎯 Use Cases

- **Express Workflow QA**: Automate repetitive QA checks on high-volume projects
- **Regression Testing**: Automatically test all features after code changes
- **New Feature Validation**: AI explores and tests new functionality
- **Cross-Browser Testing**: Run tests across different browser configurations
- **CI/CD Integration**: Add as automated quality gate in deployment pipeline

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   PLANNER    │───▶│    RUNNER    │───▶│WRIKE POSTER  │
│    Agent     │    │    Agent     │    │    Node      │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
  Test Plans         Test Report         Wrike Report
  (Markdown)         + Screenshots       (Formatted)
```

### Workflow Nodes

1. **Planner Agent**
   - Explores web application using Playwright
   - Takes screenshots to understand UI structure
   - Generates test scenarios as markdown files
   - Saves to: `qa_workspace/plans/`

2. **Runner Agent**
   - Reads test plans from planner
   - Executes tests using Playwright automation
   - Captures screenshots at each step
   - Generates comprehensive test report
   - Saves to: `qa_workspace/reports/` and `qa_workspace/screenshots/`

3. **Wrike Poster Node** (Optional)
   - Formats test report for Wrike
   - Includes: build info, environment, test type, pass/fail summary, defects
   - Posts to Wrike task (demo or production mode)
   - Saves formatted report for audit trail
   - Saves to: `qa_workspace/wrike_reports/`

---

## 🔧 Technology Stack

- **AI Framework**: LangChain, LangGraph, DeepAgents
- **Language Model**: OpenAI GPT-4o (vision + reasoning)
- **Browser Automation**: Playwright (via MCP protocol)
- **Workflow Engine**: LangGraph (state management, conditional routing)
- **Language**: Python 3.13+
- **Package Manager**: UV (fast Python package management)

---

## 📦 What's Included

### Core Components
- ✅ Multi-agent QA system with LangGraph orchestration
- ✅ AI-powered test planning and execution
- ✅ Browser automation with persistent sessions
- ✅ Screenshot capture and evidence collection
- ✅ Wrike integration with formatted reports
- ✅ Complete audit trail system

### Test Applications
- ✅ React Vet Clinic Dashboard (primary test app)
- ✅ Static HTML application (backup)

---

## 📊 Sample Outputs

### Test Report (`qa_workspace/reports/test_report.md`)
```markdown
# Test Execution Report

## Summary
- **Total Tests Executed**: 5
- **Passed**: 2
- **Failed**: 3

## Details
### Homepage Load Test
- **Status**: PASS
- **Screenshots**: [initial.png, final.png]
...
```

### Wrike Report (`qa_workspace/wrike_reports/wrike_report_*.txt`)
```
🤖 Zero-Touch QA Report
============================================================

📦 Build / Version: v1.0.0
🌐 Environment: dev
🔁 Test Type: Automated Regression
📅 Date: 2026-02-06

📊 SUMMARY
  Total Tests: 5
  ✅ Passed: 2
  ❌ Failed: 3
  🚦 Overall Status: ❌ FAIL

📋 TEST RESULTS
  ✅ 1. Homepage Load Test – PASS
  ❌ 2. Patient Creation Test – FAIL (High)
  ...

🐞 DEFECTS
  - BUG-885: Patient Creation Test failure
  ...
```

---

## 🙏 Acknowledgments

Built with:
- [LangChain](https://www.langchain.com/) - AI orchestration framework
- [LangGraph](https://www.langchain.com/langgraph) - Agent workflow engine
- [OpenAI GPT-4o](https://openai.com/) - Language model
- [Playwright](https://playwright.dev/) - Browser automation
- [DeepAgents](https://docs.langchain.com/oss/python/deepagents/overview) - Agent framework

---

**Made for hackathon submission - February 2026**
