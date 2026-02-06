from typing import Literal, Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage

from qa_agent.workspace import init_workspace, get_path, get_test_app_url
from qa_agent.agents import create_planner_agent, create_runner_agent

init_workspace()


class WorkflowState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    task_type: Literal["plan", "run", "full"]
    wrike_enabled: bool
    wrike_task_id: str


def get_user_input(state: WorkflowState) -> str:
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if hasattr(msg, "content") and msg.content:
                return msg.content
    return ""


def route_task(state: WorkflowState) -> Literal["planner", "runner"]:
    task_type = state.get("task_type", "full")
    if task_type == "run":
        return "runner"
    return "planner"


def should_continue(state: WorkflowState) -> Literal["runner", "end"]:
    task_type = state.get("task_type", "full")
    if task_type == "full":
        return "runner"
    return "end"


def should_post_to_wrike(state: WorkflowState) -> Literal["wrike_poster", "end"]:
    """Decide if we should post to Wrike after runner completes."""
    wrike_enabled = state.get("wrike_enabled", False)
    if wrike_enabled:
        return "wrike_poster"
    return "end"


def plan_tests(state: WorkflowState) -> dict:
    agent = create_planner_agent()
    plans_dir = get_path("plans")
    test_url = get_test_app_url()
    user_input = get_user_input(state)
    
    result = agent.invoke({
        "messages": [HumanMessage(content=f"""
TARGET APPLICATION: {test_url}

USER REQUEST: {user_input if user_input else "Explore and create test scenarios for all features"}

Create test scenarios based on the user's request above.
Save each test to: {plans_dir}/<test_name>.md
""")]
    })
    return {"messages": [result["messages"][-1]]}


def run_tests(state: WorkflowState) -> dict:
    agent = create_runner_agent()
    plans_dir = get_path("plans")
    reports_dir = get_path("reports")
    test_url = get_test_app_url()
    user_input = get_user_input(state)
    
    result = agent.invoke({
        "messages": [HumanMessage(content=f"""
TARGET APPLICATION: {test_url}

USER REQUEST: {user_input if user_input else "Run all available tests"}

Test files location: {plans_dir}
Save report to: {reports_dir}/test_report.md

Execute tests based on the user's request above.
""")]
    })
    return {"messages": [result["messages"][-1]]}


def post_to_wrike(state: WorkflowState) -> dict:
    """Post QA results to Wrike as a final step in the workflow."""
    from qa_agent.wrike_integration import post_qa_results_to_wrike
    
    task_id = state.get("wrike_task_id", "DEMO-TASK-001")
    report_path = get_path("reports") / "test_report.md"
    screenshots_dir = get_path("screenshots")
    
    if not report_path.exists():
        msg = f"⚠️ No test report found at {report_path}. Skipping Wrike post."
        print(msg)
        return {"messages": [AIMessage(content=msg)]}
    
    print(f"\n📤 Posting QA results to Wrike task: {task_id}")
    
    try:
        result = post_qa_results_to_wrike(
            task_id=task_id,
            report_path=report_path,
            screenshots_dir=screenshots_dir,
            attach_screenshots=True
        )
        
        status = result.get("comment", {}).get("status", "unknown")
        saved_report = result.get("saved_report", "N/A")
        
        if "success" in status:
            msg = f"""✅ Successfully posted QA report to Wrike task {task_id}

📋 Details:
  Comment ID: {result['comment'].get('comment_id', 'N/A')}
  Task Status: {result['status_update'].get('new_status', 'N/A')}
  Saved Report: {saved_report}
  
💾 Wrike report saved for audit trail"""
        else:
            msg = f"⚠️ Wrike posting completed with status: {status}"
        
        print(msg)
        return {"messages": [AIMessage(content=msg)]}
        
    except Exception as e:
        error_msg = f"❌ Error posting to Wrike: {str(e)}"
        print(error_msg)
        return {"messages": [AIMessage(content=error_msg)]}


def create_qa_workflow():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("planner", plan_tests)
    workflow.add_node("runner", run_tests)
    workflow.add_node("wrike_poster", post_to_wrike)
    
    workflow.add_conditional_edges(START, route_task, {"planner": "planner", "runner": "runner"})
    workflow.add_conditional_edges("planner", should_continue, {"runner": "runner", "end": END})
    workflow.add_conditional_edges("runner", should_post_to_wrike, {"wrike_poster": "wrike_poster", "end": END})
    workflow.add_edge("wrike_poster", END)
    
    return workflow.compile()


graph = create_qa_workflow()


def run_planner(message: str = "") -> str:
    """Run only the planner agent."""
    init_workspace()
    result = graph.invoke({
        "task_type": "plan",
        "messages": [HumanMessage(content=message)] if message else [],
        "wrike_enabled": False
    })
    return result["messages"][-1].content if result.get("messages") else ""


def run_runner() -> str:
    """Run only the runner agent (assumes test plans exist)."""
    init_workspace()
    result = graph.invoke({
        "task_type": "run",
        "messages": [],
        "wrike_enabled": False
    })
    return result["messages"][-1].content if result.get("messages") else ""


def run_full(message: str = "", post_to_wrike: bool = False, wrike_task_id: str = None) -> str:
    """Run full workflow: planner -> runner -> (optionally) wrike poster.
    
    Args:
        message: Optional message to customize the QA run
        post_to_wrike: Whether to post results to Wrike (demo mode)
        wrike_task_id: Wrike task ID to post to (e.g., "EXPRESS-2024-001")
    
    Returns:
        Final message content from the workflow
    """
    init_workspace()
    result = graph.invoke({
        "task_type": "full",
        "messages": [HumanMessage(content=message)] if message else [],
        "wrike_enabled": post_to_wrike,
        "wrike_task_id": wrike_task_id or "DEMO-TASK-001"
    })
    
    return result["messages"][-1].content if result.get("messages") else ""
