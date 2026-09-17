import json
import asyncio
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.base import call_llm
from agents.planner import Plan


class TestResult(BaseModel):
    passed: bool
    stdout: str
    stderr: str
    error: str | None = None


class TestCodeResponse(BaseModel):
    test_code: str = Field(description="The complete Pytest script.")


TESTER_SYSTEM_PROMPT = """
You are the Tester agent in a multi-agent coding team.
Your job is to read the target Python code and test hints, then write a complete, runnable Pytest script.
The test script must import from a file named `solution.py` in the same directory.
Write ONLY the Python code for the test — no markdown, no explanations.
"""


def generate_test_code(code: str, plan: Plan) -> str:
    """Generate a Pytest script for the given solution code."""
    user_prompt = (
        f"Target Code (`solution.py`):\n<code>\n{code}\n</code>\n\n"
        f"Test Hints:\n{plan.test_hints}\n\n"
        f"Write the pytest script importing from `solution` and testing thoroughly."
    )

    response: TestCodeResponse = call_llm(
        system_prompt=TESTER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=TestCodeResponse,
    )
    return response.test_code


async def _run_mcp_sandbox(code: str, test_code: str) -> TestResult:
    """Connect to the MCP sandbox server via stdio and execute the code."""
    # Inject project root into PYTHONPATH so the subprocess finds mcp_sandbox
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
                "run_code", arguments={"code": code, "test_code": test_code}
            )
            data = json.loads(result.content[0].text)
            return TestResult(
                passed=data.get("passed", False),
                stdout=data.get("stdout", ""),
                stderr=data.get("stderr", ""),
                error=data.get("error"),
            )


def run_tests(code: str, plan: Plan) -> TestResult:
    """
    Generate tests for the given code and run them in the Docker MCP sandbox.

    Args:
        code: The solution code to test.
        plan: The Plan (used for test_hints).

    Returns:
        TestResult with pass/fail status and output.
    """
    test_code = generate_test_code(code, plan)
    return asyncio.run(_run_mcp_sandbox(code, test_code))
