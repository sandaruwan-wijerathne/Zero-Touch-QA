# LangGraph Workflow Architecture

## Workflow with Wrike Integration

```
                            START
                              |
                              v
                      [Route by task_type]
                              |
                    +---------+---------+
                    |                   |
              task="plan"         task="run"
                    |                   |
                    v                   v
            +---------------+     +---------------+
            | PLANNER NODE  |     | RUNNER NODE   |
            |               |     |               |
            | - Explores    |     | - Executes    |
            |   application |     |   test plans  |
            | - Creates     |     | - Takes       |
            |   test plans  |     |   screenshots |
            | - Saves to    |     | - Generates   |
            |   plans/      |     |   report      |
            +---------------+     +---------------+
                    |                   |
                    v                   v
            [Should continue?]    [Should post to Wrike?]
                    |                   |
              if task="full"     if wrike_enabled=True
                    |                   |
                    v                   v
            +---------------+     +------------------+
            | RUNNER NODE   |     | WRIKE POSTER     |
            |               |     |                  |
            | (same as      |     | - Reads report   |
            |  above)       |     | - Formats output |
            +---------------+     | - Posts comment  |
                    |             | - Uploads        |
                    v             |   screenshots    |
            [Should post         | - Updates status |
             to Wrike?]          +------------------+
                    |                   |
             if wrike_enabled           v
                    |                 END
                    v
            +------------------+
            | WRIKE POSTER     |
            | (same as above)  |
            +------------------+
                    |
                    v
                  END
```

## Node Descriptions

### 1. **PLANNER NODE** (`plan_tests`)
- **Purpose**: Autonomous test scenario generation
- **Input**: User request + target URL
- **Process**: AI agent explores application and creates test plans
- **Output**: Test scenarios saved as markdown files
- **Location**: `qa_workspace/plans/*.md`

### 2. **RUNNER NODE** (`run_tests`)
- **Purpose**: Test execution and reporting
- **Input**: Test plans from planner
- **Process**: AI agent executes tests, captures screenshots
- **Output**: Test report with results
- **Location**: `qa_workspace/reports/test_report.md`

### 3. **WRIKE POSTER NODE** (`post_to_wrike`) ⭐ NEW
- **Purpose**: Automated Wrike integration
- **Input**: Test report + screenshots
- **Process**: 
  - Formats report for Wrike
  - Posts as comment to specified task
  - Attaches screenshots (up to 5)
  - Updates task status based on results
- **Output**: Success/error message
- **Mode**: Demo (can be activated for production with API token)

## State Schema

```python
class WorkflowState(TypedDict):
    messages: list[BaseMessage]         # Conversation history
    task_type: Literal["plan", "run", "full"]  # Workflow mode
    wrike_enabled: bool                 # Enable Wrike posting
    wrike_task_id: str                  # Target Wrike task
```

## Conditional Logic

### `route_task()`
Routes initial workflow based on task type:
- `"plan"` → Go to PLANNER NODE
- `"run"` → Go directly to RUNNER NODE
- `"full"` → Go to PLANNER NODE (will chain to RUNNER)

### `should_continue()`
After PLANNER NODE:
- If `task_type == "full"` → Go to RUNNER NODE
- Otherwise → END

### `should_post_to_wrike()` ⭐ NEW
After RUNNER NODE:
- If `wrike_enabled == True` → Go to WRIKE POSTER NODE
- Otherwise → END

## Usage Examples

### 1. Plan Only (no Wrike)
```python
from qa_agent import run_planner

run_planner("Create tests for patient management")
```
**Flow**: START → PLANNER → END

### 2. Run Tests Only (no Wrike)
```python
from qa_agent import run_runner

run_runner()
```
**Flow**: START → RUNNER → END

### 3. Full Workflow (no Wrike)
```python
from qa_agent import run_full

run_full("Test all features")
```
**Flow**: START → PLANNER → RUNNER → END

### 4. Full Workflow + Wrike Integration ⭐
```python
from qa_agent import run_full

run_full(
    message="Test patient features",
    post_to_wrike=True,
    wrike_task_id="EXPRESS-2024-001"
)
```
**Flow**: START → PLANNER → RUNNER → WRIKE POSTER → END

## Benefits of Node-Based Architecture

✅ **Composable**: Nodes can be run independently or chained  
✅ **State Management**: LangGraph handles state persistence  
✅ **Conditional Routing**: Smart decisions based on state  
✅ **Error Handling**: Each node can fail independently  
✅ **Extensible**: Easy to add new nodes (e.g., Jotform poster)  
✅ **Traceable**: Full workflow history in messages  

## Future Extensions

Potential additional nodes:
- **Jotform Poster**: Submit QA history to Jotform
- **Slack Notifier**: Send notifications to Slack
- **Validator**: Pre-check before posting to Wrike
- **Retry Handler**: Automatic retry on failures
- **Analytics Collector**: Track QA metrics
