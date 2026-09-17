import logging
from typing import Optional

from pydantic import BaseModel

from agents.planner import generate_plan, Plan
from agents.coder import generate_code
from agents.reviewer import review_code
from agents.tester import run_tests

logger = logging.getLogger(__name__)


class PipelineResult(BaseModel):
    success: bool
    iterations: int
    final_code: Optional[str]
    failure_reason: Optional[str]


def run_pipeline(spec: str, max_iterations: int = 4) -> PipelineResult:
    """
    Run the full multi-agent coding pipeline.

    Flow: Planner → (Coder → Reviewer → Tester) loop

    Args:
        spec: Plain-English coding specification.
        max_iterations: Maximum Coder→Tester revision cycles before giving up.

    Returns:
        PipelineResult with success status, iteration count, and final code.
    """
    logger.info("Starting pipeline")

    # Step 1: Plan
    logger.info("Planner Agent is generating the plan...")
    plan = generate_plan(spec)
    logger.info(
        f"Plan generated with {len(plan.functions)} function(s) "
        f"and {len(plan.edge_cases)} edge case(s)."
    )

    code: Optional[str] = None
    feedback: Optional[str] = None

    # Steps 2–4: Coder → Reviewer → Tester loop
    for iteration in range(1, max_iterations + 1):
        logger.info(f"--- Iteration {iteration}/{max_iterations} ---")

        # Coder
        logger.info("Coder Agent is writing code...")
        code = generate_code(plan=plan, feedback=feedback, previous_code=code)

        # Reviewer
        logger.info("Reviewer Agent is checking code...")
        review = review_code(code=code, spec=spec, plan=plan)

        if not review.approved:
            logger.info(f"Reviewer rejected code. Issues: {review.issues}")
            feedback = "Code review failed with issues:\n" + "\n".join(review.issues)
            continue

        logger.info("Reviewer approved code. Moving to Tester.")

        # Tester
        logger.info("Tester Agent is writing and running tests in MCP sandbox...")
        test_result = run_tests(code=code, plan=plan)

        if test_result.passed:
            logger.info("Tests passed! Pipeline successful.")
            return PipelineResult(
                success=True,
                iterations=iteration,
                final_code=code,
                failure_reason=None,
            )

        logger.info(f"Tests failed.\nSTDOUT:\n{test_result.stdout}\nSTDERR:\n{test_result.stderr}")
        feedback = f"Tests failed.\nSTDOUT:\n{test_result.stdout}\nSTDERR:\n{test_result.stderr}"
        if test_result.error:
            feedback += f"\nERROR:\n{test_result.error}"

    logger.error("Pipeline failed: Reached max iterations without passing tests.")
    return PipelineResult(
        success=False,
        iterations=max_iterations,
        final_code=code,
        failure_reason="Reached max iterations without passing tests.",
    )
