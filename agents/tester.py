import json
import asyncio
import os
import sys
from typing import Dict
from pathlib import Path

from pydantic import BaseModel, Field
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.base import call_llm
from agents.planner import Plan

# The test file is always written under this key in the files dict
TEST_FILE = "test_solution.py"


class TestResult(BaseModel):
    passed: bool
    stdout: str
    stderr: str
    error: str | None = None


class _TestCodeResponse(BaseModel):
    test_code: str = Field(description="The complete Pytest script.")


TESTER_SYSTEM_PROMPT = """
You are the Tester agent in a multi-agent coding team.
Your job is to write a complete, runnable Pytest script that tests the provided solution code.

Rules:
- Import from the entry module specified (e.g. `from solution import foo` or `from calculator.core import add`).
- Write ONLY the Python test code — no markdown, no explanations.
- Cover the normal cases, edge cases, and error cases described in the test hints.
"""


def _generate_test_code(files: Dict[str, str], plan: Plan) -> str:
    """Generate a Pytest script for the given file map."""
    files_str = "\n\n".join(
        f"# === {fname} ===\n{src}" for fname, src in files.items()
    )

    user_prompt = (
        f"Solution Files:\n<code>\n{files_str}\n</code>\n\n"
        f"Entry Module to import from: `{plan.entry_module}`\n\n"
        f"Test Hints:\n{plan.test_hints}\n\n"
        f"Write the complete pytest script. "
        f"Import from `{plan.entry_module}` (not from 'solution' unless that IS the entry module)."
    )

    response: _TestCodeResponse = call_llm(
        system_prompt=TESTER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=_TestCodeResponse,
    )
    return response.test_code


async def _run_mcp_sandbox(files: Dict[str, str], test_file: str) -> TestResult:
    """Connect to the MCP sandbox server via stdio and execute the files."""
    project_root = str(Path(__file__).parent.parent)
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_sandbox.server"],
        env=env,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "run_code",
                arguments={"files": files, "test_file": test_file},
            )
            data = json.loads(result.content[0].text)
            return TestResult(
                passed=data.get("passed", False),
                stdout=data.get("stdout", ""),
                stderr=data.get("stderr", ""),
                error=data.get("error"),
            )


def run_tests(files: Dict[str, str], plan: Plan) -> TestResult:
    """
    Generate tests for the given file map and run them in the Docker MCP sandbox.

    Args:
        files: Dict of filename → source code (the solution files).
        plan: The Plan (used for entry_module and test_hints).

    Returns:
        TestResult with pass/fail status and output.
    """
    test_code = _generate_test_code(files, plan)
    all_files = {**files, TEST_FILE: test_code}
    return asyncio.run(_run_mcp_sandbox(all_files, TEST_FILE))
