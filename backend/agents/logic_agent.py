# agents/logic_agent.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
# create_openai_tools_agent, 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.llm import get_llm
from logger import get_logger

logger = get_logger(__name__)


def get_logic_agent():

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
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
"""),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    # agent = create_openai_tools_agent(llm, [], prompt)
    agent = create_tool_calling_agent(llm, [], prompt)

    return AgentExecutor(
        agent=agent,
        tools=[],
        verbose=True,
        handle_parsing_errors=True
    )