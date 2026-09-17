from typing import List

from pydantic import BaseModel, Field

from agents.base import call_llm


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


PLANNER_SYSTEM_PROMPT = """
You are the Planner agent in a multi-agent coding team.
Your job is to read a user's coding specification and break it down into a clear, structured plan.
Return your plan as JSON matching the requested schema.
Do NOT write implementation code. Only plan it.
Focus on: the functions needed, edge cases to handle, and what test scenarios are required.
"""


def generate_plan(spec: str) -> Plan:
    """
    Break a user specification into a structured Plan.

    Args:
        spec: Plain-English description of the code to write.

    Returns:
        A Plan dataclass with functions, edge_cases, and test_hints.
    """
    user_prompt = f"Here is the specification to plan:\n\n<spec>\n{spec}\n</spec>"

    plan: Plan = call_llm(
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_schema=Plan,
    )
    return plan
