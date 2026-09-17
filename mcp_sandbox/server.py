import json
import logging
from typing import Dict

from mcp.server.mcpserver import MCPServer
from mcp_sandbox.executor import run_in_docker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = MCPServer("code_sandbox")


@mcp.tool()
def run_code(files: Dict[str, str], test_file: str = "test_solution.py") -> str:
    """
    Execute a set of Python files in an isolated Docker sandbox and run pytest.

    Args:
        files: Dict mapping relative filename → Python source code.
               Must include the test script under the key matching test_file.
        test_file: Relative path of the pytest script within files.

    Returns:
        JSON string with keys: passed, stdout, stderr, error.
    """
    logger.info("Received run_code request (%d file(s), test=%s)", len(files), test_file)
    result = run_in_docker(files=files, test_file=test_file)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    logger.info("Starting Code Sandbox MCP Server (stdio)")
    mcp.run()
