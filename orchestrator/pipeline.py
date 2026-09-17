import logging
from typing import Optional, Dict

from pydantic import BaseModel

from agents.planner import generate_plan, Plan
from agents.coder import generate_code
from agents.reviewer import review_code
from agents.tester import run_tests

logger = logging.getLogger(__name__)


class PipelineResult(BaseModel):
    success: bool
    iterations: int
    final_files: Optional[Dict[str, str]]
    failure_reason: Optional[str]


def run_pipeline(spec: str, max_iterations: int = 4) -> PipelineResult:
    """
    Run the full multi-agent coding pipeline.

    Flow: Planner → (Coder → Reviewer → Tester) loop

    For simple single-function specs, the Planner will produce a single solution.py.
    For complex multi-module specs, the Planner will produce multiple files.

    Args:
        spec: Plain-English coding specification.
        max_iterations: Maximum Coder→Tester revision cycles before giving up.

    Returns:
        PipelineResult with success status, iteration count, and final file map.
    """
    logger.info("Starting pipeline")

    # Step 1: Plan
    logger.info("Planner Agent is generating the plan...")
    plan = generate_plan(spec)
    logger.info(
        "Plan generated with %d function(s), %d edge case(s), %d file(s).",
        len(plan.functions),
        len(plan.edge_cases),
        len(plan.modules),
    )

    files: Optional[Dict[str, str]] = None
    feedback: Optional[str] = None

    # Steps 2–4: Coder → Reviewer → Tester loop
    for iteration in range(1, max_iterations + 1):
        logger.info("--- Iteration %d/%d ---", iteration, max_iterations)

        # Coder
        logger.info("Coder Agent is writing code...")
        files = generate_code(plan=plan, feedback=feedback, previous_files=files)

        # Reviewer
        logger.info("Reviewer Agent is checking code...")
        review = review_code(files=files, spec=spec, plan=plan)

        if not review.approved:
            logger.info("Reviewer rejected code. Issues: %s", review.issues)
            feedback = "Code review failed:\n" + "\n".join(review.issues)
            continue

        logger.info("Reviewer approved code. Moving to Tester.")

        # Tester (runs in Docker via MCP sandbox)
        logger.info("Tester Agent is writing and running tests in MCP sandbox...")
        test_result = run_tests(files=files, plan=plan)

        if test_result.passed:
            logger.info("Tests passed! Pipeline successful.")
            return PipelineResult(
                success=True,
                iterations=iteration,
                final_files=files,
                failure_reason=None,
            )

        logger.info(
            "Tests failed.\nSTDOUT:\n%s\nSTDERR:\n%s",
            test_result.stdout,
            test_result.stderr,
        )
        feedback = (
            f"Tests failed.\nSTDOUT:\n{test_result.stdout}\n"
            f"STDERR:\n{test_result.stderr}"
        )
        if test_result.error:
            feedback += f"\nERROR:\n{test_result.error}"

    logger.error("Pipeline failed: Reached max iterations without passing tests.")
    return PipelineResult(
        success=False,
        iterations=max_iterations,
        final_files=files,
        failure_reason="Reached max iterations without passing tests.",
    )
