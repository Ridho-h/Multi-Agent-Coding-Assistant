from typing import Dict, List

from pydantic import BaseModel, Field

from agents.base import call_llm
from agents.planner import Plan


class ReviewResult(BaseModel):
    approved: bool = Field(
        description="True if code is ready for testing, False if issues were found."
    )
    issues: List[str] = Field(
        description="Specific issues the Coder must fix. Empty list if approved."
    )


REVIEWER_SYSTEM_PROMPT = """
You are the Reviewer agent in a multi-agent coding team.
You receive one or more Python source files and must evaluate them against the spec and plan.

Evaluate:
1. Does the code match the specification?
2. Are there obvious syntax errors or logical bugs?
3. Are the planned edge cases handled?
4. Do imports between files look correct?

If the code looks solid, approve it. If not, reject it with specific, actionable issues.
Be brief and constructive.
"""


def review_code(files: Dict[str, str], spec: str, plan: Plan) -> ReviewResult:
    """
    Review all generated files against the original spec and plan.

    Args:
        files: Dict mapping filename → source code.
        spec: The original user specification.
        plan: The Plan from the Planner agent.

    Returns:
        ReviewResult with an approved flag and optional list of issues.
    """
    files_str = "\n\n".join(
        f"# === {fname} ===\n{src}" for fname, src in files.items()
    )

    user_prompt = (
        f"Original Specification:\n<spec>\n{spec}\n</spec>\n\n"
        f"Planned Edge Cases:\n{chr(10).join(plan.edge_cases)}\n\n"
        f"Code to Review:\n<code>\n{files_str}\n</code>\n\n"
        f"Evaluate the code and return your ReviewResult."
    )

    review: ReviewResult = call_llm(
        system_prompt=REVIEWER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=ReviewResult,
    )
    return review
