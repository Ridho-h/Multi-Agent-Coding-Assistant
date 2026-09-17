import logging
from mcp.server.mcpserver import MCPServer
from mcp_sandbox.executor import run_in_docker
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCPServer (MCP 2.x replaces FastMCP)
mcp = MCPServer("code_sandbox")

@mcp.tool()
def run_code(code: str, test_code: str) -> str:
    """
    Executes Python code along with a test script in an isolated Docker sandbox.

    Args:
        code: The Python solution code to be tested.
        test_code: The pytest script to test the solution. It should import the solution.

    Returns:
        A JSON string containing the test results: passed, failed, stdout, stderr, and error.
    """
    logger.info("Received run_code request")
    result = run_in_docker(code, test_code)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    logger.info("Starting Code Sandbox MCP Server (stdio)")
    mcp.run()
