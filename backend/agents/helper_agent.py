# agents/helper_agent.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
# create_openai_tools_agent,
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.llm import get_llm
from logger import get_logger

def get_helper_agent():

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
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
"""),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    # agent = create_openai_tools_agent(llm, [], prompt)
    agent = create_tool_calling_agent(llm, [], prompt)

    return AgentExecutor(agent=agent, tools=[], verbose=True)