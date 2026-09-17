import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Docker image with pytest pre-installed (built via: docker build -t code-sandbox:latest ./mcp_sandbox)
SANDBOX_IMAGE = "code-sandbox:latest"


def run_in_docker(code: str, test_code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute solution code and tests inside an isolated Docker container.

    The container runs with:
      - --network none  (no internet access for generated code)
      - --memory 128m   (prevents memory exhaustion)
      - --cpus 0.5      (prevents CPU exhaustion)

    Args:
        code: The Python solution code.
        test_code: The Pytest test script (imports from solution.py).
        timeout: Max seconds before the container is killed.

    Returns:
        Dict with keys: passed (bool), failed (bool), stdout (str), stderr (str), error (str | None).
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "solution.py").write_text(code, encoding="utf-8")
        (tmp_path / "test_solution.py").write_text(test_code, encoding="utf-8")

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "-v", f"{tmp_path.absolute()}:/code",
            "-w", "/code",
            SANDBOX_IMAGE,
            "python", "-m", "pytest", "test_solution.py", "-v",
        ]

        logger.debug("Sandbox command: %s", " ".join(docker_cmd))

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            passed = result.returncode == 0
            return {
                "passed": passed,
                "failed": not passed,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "failed": True,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds.",
                "error": "TimeoutExpired",
            }
        except Exception as exc:
            return {
                "passed": False,
                "failed": True,
                "stdout": "",
                "stderr": str(exc),
                "error": type(exc).__name__,
            }
