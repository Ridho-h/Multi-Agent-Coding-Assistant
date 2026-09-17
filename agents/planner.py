from typing import List

from pydantic import BaseModel, Field

from agents.base import call_llm


class FileSpec(BaseModel):
    """Describes a single file the Coder should produce."""

    filename: str = Field(
        description="Relative file path, e.g. 'solution.py' or 'calculator/core.py'."
    )
    purpose: str = Field(
        description="What this file contains and why it exists."
    )


class Plan(BaseModel):
    functions: List[str] = Field(
        description="List of function signatures to implement."
    )
    edge_cases: List[str] = Field(
        description="Edge cases the implementation must handle."
    )
    test_hints: str = Field(
        description="Description of what the tests should verify."
    )
    modules: List[FileSpec] = Field(
        description=(
            "Files to generate. For simple single-function specs use a single "
            "FileSpec with filename='solution.py'. Only use multiple files when "
            "the spec clearly requires separate modules or packages."
        )
    )
    entry_module: str = Field(
        description=(
            "Python dotted module path that tests should import from. "
            "e.g. 'solution' for solution.py, or 'calculator.core' for calculator/core.py."
        )
    )


PLANNER_SYSTEM_PROMPT = """
You are the Planner agent in a multi-agent coding team.
Your job is to read a user's coding specification and produce a structured plan.

Rules:
- For simple, single-function specs: use ONE file named 'solution.py' and entry_module='solution'.
- Only use multiple files when the spec explicitly requests separate modules or packages.
- Do NOT write implementation code. Only plan it.
- Focus on: functions needed, edge cases, test requirements, and module layout.

Return your plan as JSON matching the requested schema.
"""


def generate_plan(spec: str) -> Plan:
    """
    Break a user specification into a structured Plan.

    Args:
        spec: Plain-English description of the code to write.

    Returns:
        A Plan with functions, edge_cases, test_hints, modules, and entry_module.
    """
    user_prompt = f"Here is the specification to plan:\n\n<spec>\n{spec}\n</spec>"

    plan: Plan = call_llm(
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=Plan,
    )
    return plan
