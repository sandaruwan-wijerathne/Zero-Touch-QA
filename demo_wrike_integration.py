#!/usr/bin/env python3
"""Demo script showing Wrike integration functionality.

This demonstrates how QA reports would be posted to Wrike tasks
in a production environment (currently in demo/mock mode).
"""

from pathlib import Path
from qa_agent.workspace import init_workspace, get_path
from qa_agent.wrike_integration import post_qa_results_to_wrike, WrikeIntegration


def demo_basic_comment():
    """Demo: Post a QA report as a Wrike comment."""
    print("\n" + "="*70)
    print("DEMO 1: Basic QA Report Comment")
    print("="*70)
    
    init_workspace()
    
    # Use existing test report
    report_path = get_path("/home/vetstoria/Downloads/qa/zero_toutch_qa_final_version/qa_workspace/reports") / "test_report.md"
    screenshots_dir = get_path("/home/vetstoria/Downloads/qa/zero_toutch_qa_final_version/qa_workspacescreenshots")
    
    if not report_path.exists():
        print("⚠️  No test report found. Run QA tests first:")
        print("   python -m qa_agent.orchestrator")
        return
    
    # Post to mock Wrike task
    result = post_qa_results_to_wrike(
        task_id="EXPRESS-2024-001",
        report_path=report_path,
        screenshots_dir=screenshots_dir,
        attach_screenshots=True
    )
    
    print(f"\n✅ Result: {result['comment']['message']}")


def demo_custom_workflow():
    """Demo: Custom workflow with multiple Wrike operations."""
    print("\n" + "="*70)
    print("DEMO 2: Multi-Step Wrike Workflow")
    print("="*70)
    
    wrike = WrikeIntegration()
    task_id = "EXPRESS-2024-002"
    
    # Step 1: Post initial comment
    print("\n📝 Step 1: Posting 'QA Started' comment...")
    wrike.post_comment(
        task_id,
        "🤖 Zero-Touch QA initiated\n\nStatus: Tests running...\nEstimated time: 15 minutes"
    )
    
    # Step 2: Update status
    print("\n🔄 Step 2: Updating task status...")
    wrike.update_task_status(task_id, "In QA")
    
    # Step 3: Post results (simulated)
    print("\n📊 Step 3: Posting test results...")
    init_workspace()
    report_path = get_path("reports") / "test_report.md"
    screenshots_dir = get_path("screenshots")
    
    if report_path.exists():
        formatted_report = wrike.format_qa_report(report_path, screenshots_dir)
        wrike.post_comment(task_id, formatted_report)
    else:
        wrike.post_comment(
            task_id,
            "✅ QA Complete\n\nTests: 7/7 passed\nNo issues found"
        )
    
    # Step 4: Final status update
    print("\n✅ Step 4: Marking QA complete...")
    wrike.update_task_status(task_id, "QA Approved")
    
    print("\n" + "="*70)
    print("Demo complete! In production, these would be real Wrike API calls.")
    print("="*70)


def demo_production_setup():
    """Show how to set up for production use."""
    print("\n" + "="*70)
    print("PRODUCTION SETUP GUIDE")
    print("="*70)
    
    print("""
To use with real Wrike API:

1. Get Wrike API token:
   - Log into Wrike
   - Go to Account Settings > Apps & Integrations > API
   - Generate permanent access token

2. Set environment variable:
   export WRIKE_API_TOKEN="your-token-here"
   
   Or add to .env file:
   WRIKE_API_TOKEN=your-token-here

3. Update wrike_integration.py to use real API:
   - Uncomment the requests.post() code
   - Remove demo mode logic
   - Add error handling

4. Test with real task:
   from qa_agent import post_qa_results_to_wrike
   
   post_qa_results_to_wrike(
       task_id="YOUR-TASK-ID",
       report_path=Path("qa_workspace/reports/test_report.md"),
       screenshots_dir=Path("qa_workspace/screenshots")
   )

API Documentation:
https://developers.wrike.com/api/v4/comments/
""")
    
    print("="*70)


def main():
    """Run all demos."""
    print("\n🚀 ZERO-TOUCH QA - WRIKE INTEGRATION DEMO")
    print("="*70)
    print("This demonstrates how QA reports are automatically posted to Wrike.")
    print("Currently running in DEMO MODE (no actual API calls).")
    print("="*70)
    
    # Demo 1: Basic comment posting
    demo_basic_comment()
    
    # Demo 2: Multi-step workflow
    demo_custom_workflow()
    
    # Demo 3: Production setup info
    demo_production_setup()
    
    print("\n✅ All demos complete!\n")


if __name__ == "__main__":
    main()
