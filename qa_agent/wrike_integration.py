"""Wrike integration for posting QA reports.

This is a mock implementation for demonstration purposes.
For production, replace with actual Wrike API calls using requests library.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class WrikeIntegration:
    """Mock Wrike integration for demonstration."""
    
    def __init__(self, api_token: str = None):
        """Initialize Wrike integration.
        
        Args:
            api_token: Wrike API token (optional for demo mode)
        """
        self.api_token = api_token or os.environ.get("WRIKE_API_TOKEN")
        self.demo_mode = not self.api_token
        
    def format_qa_report(self, report_path: Path, screenshots_dir: Path) -> str:
        """Format QA report for Wrike comment.
        
        Args:
            report_path: Path to markdown report
            screenshots_dir: Path to screenshots directory
            
        Returns:
            Formatted Wrike comment text
        """
        with open(report_path, 'r') as f:
            report_content = f.read()
        
        # Parse report for summary and details
        lines = report_content.split('\n')
        
        # Extract summary stats
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Extract test details
        test_results = []
        defects = []
        current_test = None
        test_number = 1
        
        for line in lines:
            # Extract summary numbers
            if '**Total Tests' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    total_tests = parts[1].strip().rstrip('*').strip()
            elif '**Passed' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    passed_tests = parts[1].strip().rstrip('*').strip()
            elif '**Failed' in line or '**Incomplete' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    failed_tests = parts[1].strip().rstrip('*').strip()
            
            # Extract test names and statuses
            if line.startswith('### '):
                current_test = line.replace('### ', '').strip()
                # Remove leading numbers if present (e.g., "1. Test Name" -> "Test Name")
                if current_test and current_test[0].isdigit() and '. ' in current_test:
                    current_test = current_test.split('. ', 1)[1] if '. ' in current_test else current_test
            elif current_test and '**Status**' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    status = parts[1].strip().rstrip('*').strip()
                    # Determine emoji
                    if status.lower() in ['pass', 'passed']:
                        emoji = '✅'
                        severity = ''
                    elif status.lower() in ['fail', 'failed']:
                        emoji = '❌'
                        severity = ' (High)'
                    else:
                        emoji = '⚠️'
                        severity = ' (Medium)'
                    
                    test_results.append(f"{emoji} {test_number}. {current_test} – {status.upper()}{severity}")
                    test_number += 1
                    
                    # Track defects for failed tests
                    if status.lower() in ['fail', 'failed']:
                        defect_id = f"BUG-{hash(current_test) % 1000:03d}"
                        defects.append(f"  - {defect_id}: {current_test} failure")
                    
                    current_test = None
        
        # Build test results list
        results_section = "\n  ".join(test_results[:10]) if test_results else "No test details available"
        
        # Build defects section
        defects_section = "\n".join(defects[:5]) if defects else "  - No defects found"
        
        # Count screenshots
        screenshot_count = 0
        if screenshots_dir.exists():
            screenshot_count = len(list(screenshots_dir.glob("*.png")))
        
        # Determine overall status
        try:
            passed = int(passed_tests)
            failed = int(failed_tests)
            if failed == 0:
                overall_status = "✅ PASS"
                notes = "  - All tests passed successfully\n  - Ready for next phase"
            else:
                overall_status = "❌ FAIL"
                if failed > 2:
                    notes = "  - Multiple failures detected\n  - Review required before proceeding"
                else:
                    notes = "  - Minor issues identified\n  - Re-run recommended after fixes"
        except:
            overall_status = "⚠️ PENDING"
            notes = "  - Test execution incomplete"
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_only = datetime.now().strftime('%Y-%m-%d')
        
        # Format for Wrike
        formatted = f"""🤖 Zero-Touch QA Report
{'='*60}

📦 Build / Version: v1.0.0
🌐 Environment: dev
🔁 Test Type: Automated Regression
📅 Date: {date_only}

📊 SUMMARY
  Total Tests: {total_tests}
  ✅ Passed: {passed_tests}
  ❌ Failed: {failed_tests}
  🚦 Overall Status: {overall_status}

📋 TEST RESULTS
  {results_section}

🐞 DEFECTS
{defects_section}

📸 EVIDENCE
  Screenshots: {screenshot_count} captured
  Location: {screenshots_dir.name}/

📄 FULL REPORT
  File: {report_path.name}
  Link: [View detailed report]

📝 NOTES
{notes}

⏱️ Generated: {timestamp}
{'='*60}
"""
        return formatted
    
    def post_comment(self, task_id: str, comment_text: str, attachments: list[Path] = None) -> Dict[str, Any]:
        """Post comment to Wrike task.
        
        Args:
            task_id: Wrike task ID
            comment_text: Comment text to post
            attachments: Optional list of file paths to attach
            
        Returns:
            Response dictionary with status
        """
        if self.demo_mode:
            return self._mock_post_comment(task_id, comment_text, attachments)
        
        # Production implementation would use Wrike API:
        # import requests
        # response = requests.post(
        #     f"https://www.wrike.com/api/v4/tasks/{task_id}/comments",
        #     headers={"Authorization": f"Bearer {self.api_token}"},
        #     json={"text": comment_text}
        # )
        # return response.json()
        
        return {"status": "error", "message": "API token required for production mode"}
    
    def _mock_post_comment(self, task_id: str, comment_text: str, attachments: list[Path] = None) -> Dict[str, Any]:
        """Mock implementation of posting comment."""
        print(f"\n{'='*60}")
        print(f"[DEMO MODE] Would post to Wrike task: {task_id}")
        print(f"{'='*60}")
        print(comment_text)
        if attachments:
            print(f"\n📎 Attachments ({len(attachments)}):")
            for att in attachments:
                print(f"   - {att.name}")
        print(f"{'='*60}\n")
        
        return {
            "status": "success_demo",
            "task_id": task_id,
            "comment_id": f"mock_comment_{datetime.now().timestamp()}",
            "message": "Demo mode: Comment displayed above (not actually posted to Wrike)"
        }
    
    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """Update Wrike task status.
        
        Args:
            task_id: Wrike task ID
            status: New status (e.g., "QA Complete", "Issues Found")
            
        Returns:
            Response dictionary with status
        """
        if self.demo_mode:
            print(f"[DEMO MODE] Would update task {task_id} status to: {status}")
            return {
                "status": "success_demo",
                "task_id": task_id,
                "new_status": status,
                "message": "Demo mode: Status not actually updated"
            }
        
        # Production implementation would use Wrike API
        return {"status": "error", "message": "API token required for production mode"}
    
    def add_task_attachment(self, task_id: str, file_path: Path) -> Dict[str, Any]:
        """Add attachment to Wrike task.
        
        Args:
            task_id: Wrike task ID
            file_path: Path to file to attach
            
        Returns:
            Response dictionary with status
        """
        if self.demo_mode:
            print(f"[DEMO MODE] Would attach {file_path.name} to task {task_id}")
            return {
                "status": "success_demo",
                "task_id": task_id,
                "file": file_path.name,
                "message": "Demo mode: File not actually attached"
            }
        
        # Production implementation would use Wrike API
        return {"status": "error", "message": "API token required for production mode"}


def post_qa_results_to_wrike(
    task_id: str,
    report_path: Path,
    screenshots_dir: Path,
    attach_screenshots: bool = False
) -> Dict[str, Any]:
    """Post QA results to Wrike task.
    
    This is a convenience function that handles the full workflow:
    1. Format the report
    2. Save formatted report to wrike_reports/
    3. Post as comment
    4. Optionally attach screenshots
    5. Update task status
    
    Args:
        task_id: Wrike task ID
        report_path: Path to QA report
        screenshots_dir: Path to screenshots directory
        attach_screenshots: Whether to attach screenshots (default: False)
        
    Returns:
        Dictionary with operation results
    """
    from qa_agent.workspace import get_path
    
    wrike = WrikeIntegration()
    
    # Format report
    comment_text = wrike.format_qa_report(report_path, screenshots_dir)
    
    # Save formatted report to wrike_reports directory
    wrike_reports_dir = get_path("wrike_reports")
    wrike_reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    wrike_report_filename = f"wrike_report_{task_id}_{timestamp}.txt"
    wrike_report_path = wrike_reports_dir / wrike_report_filename
    
    # Save the formatted report
    with open(wrike_report_path, 'w') as f:
        f.write(comment_text)
    
    print(f"💾 Saved Wrike report to: {wrike_report_path}")
    
    # Post comment
    comment_result = wrike.post_comment(task_id, comment_text)
    
    # Optionally attach screenshots
    attachments = []
    if attach_screenshots and screenshots_dir.exists():
        screenshot_files = list(screenshots_dir.glob("*.png"))[:5]  # Limit to 5
        for screenshot in screenshot_files:
            att_result = wrike.add_task_attachment(task_id, screenshot)
            attachments.append(att_result)
    
    # Update status based on report content
    with open(report_path, 'r') as f:
        content = f.read()
    
    if "Failed: 0" in content or "PASSED" in content:
        status = "QA Complete - Passed"
    else:
        status = "QA Complete - Issues Found"
    
    status_result = wrike.update_task_status(task_id, status)
    
    return {
        "comment": comment_result,
        "attachments": attachments,
        "status_update": status_result,
        "saved_report": str(wrike_report_path)
    }
