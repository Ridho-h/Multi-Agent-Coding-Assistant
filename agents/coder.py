from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from agents.base import call_llm
from agents.planner import Plan


class _FileContent(BaseModel):
    filename: str = Field(description="Relative file path matching the plan's FileSpec.")
    code: str = Field(description="Complete Python source for this file. No markdown fences.")


class _MultiFileCode(BaseModel):
    files: List[_FileContent] = Field(
        description="One entry per file specified in the plan's modules list."
    )


CODER_SYSTEM_PROMPT = """
You are the Coder agent in a multi-agent coding team.
Your job is to read a structured Plan and write complete, runnable Python code for every file listed in the plan's modules.

Rules:
- Produce exactly one code entry per file in the plan's modules list.
- Return ONLY Python source code in each 'code' field. No markdown fences, no explanations.
- If you receive feedback, update the relevant files to fix the reported issues.
- Ensure files can import from each other using standard relative or absolute imports.
"""


def generate_code(
    plan: Plan,
    feedback: Optional[str] = None,
    previous_files: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Generate Python source files from a plan, optionally incorporating feedback.

    Args:
        plan: The structured Plan from the Planner agent.
        feedback: Optional feedback from the Reviewer or Tester.
        previous_files: Previous file map to revise (if any).

    Returns:
        Dict mapping filename → Python source code.
    """
    modules_desc = "\n".join(
        f"  - {fs.filename}: {fs.purpose}" for fs in plan.modules
    )

    user_prompt = (
        f"Plan:\n"
        f"Functions:\n{chr(10).join(plan.functions)}\n\n"
        f"Edge Cases:\n{chr(10).join(plan.edge_cases)}\n\n"
        f"Files to produce:\n{modules_desc}\n\n"
    )

    if previous_files:
        prev_str = "\n\n".join(
            f"# --- {fname} ---\n{src}" for fname, src in previous_files.items()
        )
        user_prompt += f"Previous code:\n\n{prev_str}\n\n"

    if feedback:
        user_prompt += f"Feedback to fix:\n\n<feedback>\n{feedback}\n</feedback>\n\n"

    user_prompt += (
        f"Produce complete code for all {len(plan.modules)} file(s). "
        f"Return one entry per file."
    )

    response: _MultiFileCode = call_llm(
        system_prompt=CODER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=_MultiFileCode,
    )

    return {fc.filename: fc.code for fc in response.files}
