from langchain.agents import create_agent
from core.llm import get_llm
from logger import get_logger

logger = get_logger(__name__)


def get_helper_agent():

    llm = get_llm()

    return create_agent(
        model=llm,
        tools=[],
        system_prompt="""
You are a Helper Selection Agent.

-----------------------------------
INPUT
-----------------------------------
You receive:
- logic (structured rules)
- helpers (available helper functions)

-----------------------------------
TASK
-----------------------------------

For EACH rule:
1. Select the BEST matching helper
2. Map correct parameters
3. Generate helper call expression

-----------------------------------
RULES
-----------------------------------

- DO NOT assume helper names
- DO NOT reuse example helper names
- ONLY use helpers provided
- Match based on:
  - name
  - parameter signature

For each helper:
- helper.name → function name
- helper.params → parameters to fill

Example:
helper:
{
  "name": "hasStateCd",
  "params": ["data", "stateCd"]
}

Expression:
hasStateCd(data, "MI")

-----------------------------------
OUTPUT
-----------------------------------

Return ONLY JSON:

{{
  "expressions": [
    "<helper_call_expression_1>",
    "<helper_call_expression_2>"
  ]
}}

-----------------------------------
IMPORTANT
-----------------------------------

- Expressions MUST be constructed ONLY using provided helpers
- DO NOT reuse example helper names
- DO NOT assume helper names
- Use helper.name and helper.params strictly
"""
    )