#!/usr/bin/env python3
"""Manual script to run Zero-Touch QA workflow.

This script demonstrates how to invoke the complete QA workflow programmatically.
It runs the planner, runner, and Wrike integration in sequence.

Usage:
    python run_qa_workflow.py

Prerequisites:
    - Test application running on http://localhost:5173 (or set TEST_APP_URL)
    - OPENAI_API_KEY set in .env file
    - Dependencies installed (uv sync)
"""

from qa_agent.orchestrator import run_full


def main():
    """Execute the complete Zero-Touch QA workflow."""
    
    print("\n" + "="*70)
    print("🚀 ZERO-TOUCH QA WORKFLOW")
    print("="*70)
    print("\nThis will execute the complete QA workflow:")
    print("  1. 📝 PLANNER: Explores app and creates test scenarios")
    print("  2. ▶️  RUNNER: Executes tests and captures screenshots")
    print("  3. 📤 WRIKE: Formats and saves report for Wrike")
    print("\n" + "="*70 + "\n")
    
    print("⏳ Starting workflow... (this may take 10-15 minutes)\n")
    
    # Run full workflow with Wrike integration enabled
    try:
        result = run_full(
            message="Test all patient management features including CRUD operations",
            post_to_wrike=True,
            wrike_task_id="EXPRESS-2024-001"
        )
        
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETE")
        print("="*70)
        
        print("\n📂 Generated Outputs:")
        print("  • Test Plans:      qa_workspace/plans/")
        print("  • Test Report:     qa_workspace/reports/test_report.md")
        print("  • Screenshots:     qa_workspace/screenshots/")
        print("  • Wrike Report:    qa_workspace/wrike_reports/")
        
        print("\n📊 View Results:")
        print("  cat qa_workspace/reports/test_report.md")
        print("  cat qa_workspace/wrike_reports/wrike_report_*.txt")
        
        print("\n" + "="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        print("Partial results may be available in qa_workspace/")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ WORKFLOW FAILED")
        print("="*70)
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Ensure test app is running: http://localhost:5173")
        print("  2. Check OPENAI_API_KEY is set in .env")
        print("  3. Run 'uv sync' to install dependencies")
        print("\n" + "="*70 + "\n")
        raise


if __name__ == "__main__":
    main()
