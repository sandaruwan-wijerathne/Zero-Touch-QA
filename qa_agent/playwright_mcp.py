"""Playwright MCP integration with persistent browser session.

Uses a dedicated background thread with its own event loop to maintain
the MCP connection and browser session across all tool calls.
"""

import os
import re
import shutil
import asyncio
import threading
import queue
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool, tool
from pydantic import create_model, Field


class MCPBackgroundThread:
    """Runs MCP client in a dedicated background thread with persistent connection."""
    
    def __init__(self):
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._session: ClientSession | None = None
        self._context = None
        self._ready = threading.Event()
        self._request_queue = queue.Queue()
        self._running = False
    
    def start(self):
        """Start the background thread."""
        if self._thread is not None:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=60)  # Wait for connection
    
    def _run_loop(self):
        """Run the event loop in background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._connect_and_serve())
        finally:
            self._loop.close()
    
    async def _connect_and_serve(self):
        """Connect to MCP and process requests."""
        server = StdioServerParameters(
            command="npx",
            args=["@playwright/mcp@latest"],
            env=os.environ.copy(),
        )
        
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self._session = session
                self._ready.set()
                
                # Process requests until stopped
                while self._running:
                    try:
                        # Check for requests (non-blocking)
                        try:
                            request = self._request_queue.get_nowait()
                        except queue.Empty:
                            await asyncio.sleep(0.1)
                            continue
                        
                        method, args, result_queue = request
                        
                        try:
                            if method == "call_tool":
                                result = await session.call_tool(args["name"], args.get("arguments", {}))
                                if hasattr(result, 'content'):
                                    texts = [item.text for item in result.content if hasattr(item, 'text')]
                                    result_queue.put(("\n".join(texts) if texts else str(result), None))
                                else:
                                    result_queue.put((str(result), None))
                            
                            elif method == "list_tools":
                                result = await session.list_tools()
                                tools = [
                                    {
                                        "name": t.name,
                                        "description": getattr(t, "description", "") or "",
                                        "inputSchema": getattr(t, "inputSchema", {}) or {},
                                    }
                                    for t in result.tools
                                ]
                                result_queue.put((tools, None))
                        
                        except Exception as e:
                            result_queue.put((None, e))
                    
                    except Exception as e:
                        print(f"MCP loop error: {e}")
    
    def call_tool(self, name: str, arguments: dict[str, Any] = None) -> str:
        """Call an MCP tool (thread-safe)."""
        self.start()
        
        result_queue = queue.Queue()
        self._request_queue.put(("call_tool", {"name": name, "arguments": arguments or {}}, result_queue))
        
        result, error = result_queue.get(timeout=120)
        if error:
            raise error
        return result
    
    def list_tools(self) -> list[dict]:
        """List MCP tools (thread-safe)."""
        self.start()
        
        result_queue = queue.Queue()
        self._request_queue.put(("list_tools", {}, result_queue))
        
        result, error = result_queue.get(timeout=60)
        if error:
            raise error
        return result
    
    def stop(self):
        """Stop the background thread."""
        self._running = False


# Global background client
_mcp = MCPBackgroundThread()


def _create_langchain_tool(tool_info: dict) -> StructuredTool:
    """Create a LangChain tool."""
    name = tool_info["name"]
    description = tool_info["description"]
    schema = tool_info.get("inputSchema", {})
    
    # Build fields
    fields = {}
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    type_map = {"string": str, "integer": int, "number": float, "boolean": bool, "array": list, "object": dict}
    
    for prop_name, prop_schema in properties.items():
        py_type = type_map.get(prop_schema.get("type", "string"), str)
        prop_desc = prop_schema.get("description", "")
        
        if prop_name in required:
            fields[prop_name] = (py_type, Field(description=prop_desc))
        else:
            fields[prop_name] = (py_type | None, Field(default=None, description=prop_desc))
    
    def make_sync_fn(tool_name: str):
        def fn(**kwargs) -> str:
            args = {k: v for k, v in kwargs.items() if v is not None}
            return _mcp.call_tool(tool_name, args)
        return fn
    
    ArgsModel = create_model(f"{name}_args", **fields) if fields else create_model(f"{name}_args")
    
    return StructuredTool(
        name=name,
        description=description or f"Playwright MCP: {name}",
        func=make_sync_fn(name),
        args_schema=ArgsModel,
    )


def _get_screenshots_dir() -> Path:
    """Get the screenshots directory path."""
    from qa_agent.workspace import get_path
    return get_path("screenshots")


def _copy_screenshot_to_workspace(temp_path: str, filename: str) -> str:
    """Copy screenshot from temp to workspace."""
    screenshots_dir = _get_screenshots_dir()
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    if not filename.endswith('.png'):
        filename = f"{filename}.png"
    
    dest_path = screenshots_dir / filename
    
    if os.path.exists(temp_path):
        shutil.copy2(temp_path, dest_path)
        return str(dest_path)
    
    return f"Screenshot saved (temp): {temp_path}"


def save_screenshot(name: str) -> str:
    """Take a screenshot and save it to the workspace screenshots folder.
    
    Args:
        name: Descriptive name for the screenshot (e.g., 'login_step1_initial')
    
    Returns:
        Path to the saved screenshot in the workspace.
    """
    result = _mcp.call_tool("browser_take_screenshot", {"name": name})
    
    # Extract temp file path from MCP response (e.g., /tmp/playwright-mcp-output/1234567/screenshot.png)
    match = re.search(r'/tmp/playwright-mcp-output/\d+/[^\s\)\]]+\.png', result)
    if match:
        temp_path = match.group(0)
        saved_path = _copy_screenshot_to_workspace(temp_path, name)
        return f"Screenshot saved: {saved_path}"
    
    # If no temp path found, return the raw result for debugging
    return f"Screenshot taken but could not copy to workspace. MCP response: {result}"


def _create_save_screenshot_tool() -> StructuredTool:
    """Create the custom save_screenshot tool."""
    return StructuredTool(
        name="save_screenshot",
        description="Take a screenshot and save it to qa_workspace/screenshots/ folder. Use descriptive names like 'login_test_step1_initial' or 'form_test_error_state'.",
        func=save_screenshot,
        args_schema=create_model("save_screenshot_args", name=(str, Field(description="Descriptive name for the screenshot without extension"))),
    )


def get_tools() -> list[StructuredTool]:
    """Get all Playwright MCP tools plus custom screenshot tool."""
    global _tools_cache
    if _tools_cache is not None:
        return _tools_cache
    
    try:
        tools_info = _mcp.list_tools()
        _tools_cache = [_create_langchain_tool(info) for info in tools_info]
        _tools_cache.append(_create_save_screenshot_tool())
        print(f"Loaded {len(_tools_cache)} tools (including custom save_screenshot)")
        return _tools_cache
    except Exception as e:
        print(f"Warning: Could not load Playwright MCP tools: {e}")
        return [_create_save_screenshot_tool()]


_tools_cache = None
