# agents/logic_agent.py

from langchain.agents import create_agent
from core.llm import get_llm
from logger import get_logger

logger = get_logger(__name__)


def get_logic_agent():

    llm = get_llm()

    return create_agent(
        model=llm,
        tools=[],
        system_prompt="""
You are a Rule Logic Builder.

You will receive conditions that are ALREADY enriched with:
- oid
- path (JSON path from OSARI)
- entity

-----------------------------------
IMPORTANT
-----------------------------------

You MUST preserve:
- oid
- path
- entity

DO NOT drop them.

-----------------------------------
RULES
-----------------------------------

1. Top-level logic is always "AND"

2. Convert conditions into structured rules

-----------------------------------
TYPE MAPPING
-----------------------------------

- If oid exists → type = "coverage"
- If attribute contains "state" → type = "state"
- If path indicates policy date → type = "effective_date"

-----------------------------------
STATE HANDLING
-----------------------------------

If "states" list is provided:
- create ONE rule:
  type = "state"
  operator = "IN"
  values = states

DEFAULT OPERATORS:
- coverage → "="
- state → "IN"
- effective_date → ">="

-----------------------------------
OUTPUT FORMAT
-----------------------------------

{{
  "logic": "AND",
  "rules": [
    {
      "type": "",
      "oid": "",
      "path": "",
      "entity": "",
      "operator": "",
      "value": "",
      "values": []
    }
  ]
}}

Return ONLY JSON.
"""
    )