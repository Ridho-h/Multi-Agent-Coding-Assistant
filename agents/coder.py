from typing import Optional

from pydantic import BaseModel, Field

from agents.base import call_llm
from agents.planner import Plan


class CodeResponse(BaseModel):
    code: str = Field(
        description="The complete, runnable Python code implementation. No markdown formatting."
    )


CODER_SYSTEM_PROMPT = """
You are the Coder agent in a multi-agent coding team.
Your job is to read a structured Plan and write complete, runnable Python code that satisfies it.
If you receive feedback (from tests or reviewers), update your code to fix the issues mentioned.
Return ONLY the Python code in the 'code' field. Do not include markdown fences or explanations.
"""


def generate_code(
    plan: Plan,
    feedback: Optional[str] = None,
    previous_code: Optional[str] = None,
) -> str:
    """
    Generate Python code from a plan, optionally incorporating feedback.

    Args:
        plan: The structured Plan from the Planner agent.
        feedback: Optional feedback string from Reviewer or Tester.
        previous_code: The previous code attempt to revise (if any).

    Returns:
        Raw Python code as a string.
    """
    user_prompt = (
        f"Here is the Plan:\n\n"
        f"Functions:\n{chr(10).join(plan.functions)}\n\n"
        f"Edge Cases:\n{chr(10).join(plan.edge_cases)}\n\n"
    )

    if previous_code:
        user_prompt += f"Your previous code attempt:\n\n<code>\n{previous_code}\n</code>\n\n"

    if feedback:
        user_prompt += f"Feedback to fix:\n\n<feedback>\n{feedback}\n</feedback>\n\n"

    user_prompt += "Provide the complete, updated Python code."

    response: CodeResponse = call_llm(
        system_prompt=CODER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=CodeResponse,
    )
    return response.code
