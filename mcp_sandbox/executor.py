import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Docker image with pytest pre-installed (build via: docker build -t code-sandbox:latest ./mcp_sandbox)
SANDBOX_IMAGE = "code-sandbox:latest"


def run_in_docker(
    files: Dict[str, str],
    test_file: str = "test_solution.py",
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Write all files to a temp directory and run pytest inside an isolated Docker container.

    The container runs with:
      - --network none  (no internet access for generated code)
      - --memory 128m   (prevents memory exhaustion)
      - --cpus 0.5      (prevents CPU exhaustion)

    Subdirectories are created automatically (e.g. 'calculator/core.py' → creates calculator/).

    Args:
        files: Dict of relative filename → source code.
               Must include the test file under the key matching test_file.
        test_file: Relative path of the pytest script within files.
        timeout: Max seconds before the container is killed.

    Returns:
        Dict with keys: passed (bool), stdout (str), stderr (str), error (str | None).
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        for filename, content in files.items():
            dest = tmp_path / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

            # Create __init__.py for any new package directories
            for parent in dest.parents:
                if parent == tmp_path:
                    break
                init = parent / "__init__.py"
                if not init.exists():
                    init.touch()

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "-v", f"{tmp_path.absolute()}:/code",
            "-w", "/code",
            SANDBOX_IMAGE,
            "python", "-m", "pytest", test_file, "-v",
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
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds.",
                "error": "TimeoutExpired",
            }
        except Exception as exc:
            return {
                "passed": False,
                "stdout": "",
                "stderr": str(exc),
                "error": type(exc).__name__,
            }
