from langchain.agents import create_agent
from core.llm import get_llm
from tools.osari_tool import resolve_oids
from logger import get_logger

logger = get_logger(__name__)

def get_rule_agent():
    llm = get_llm()

    return create_agent(
        model=llm,
        tools=[resolve_oids],
        system_prompt="""
You are a Rule Processing Agent.

-----------------------------------
INPUT
-----------------------------------
You will receive a JSON input containing:
- rule intent
- conditions with OIDs

-----------------------------------
TASK
-----------------------------------
1. ALWAYS call the tool `resolve_oids`
2. Enrich each condition with:
   - oid
   - path
   - entity

3. Do NOT guess paths
4. Do NOT skip tool usage

-----------------------------------
OUTPUT (STRICT JSON)
-----------------------------------
Return ONLY:

{
  "resolved_conditions": []
}

-----------------------------------
IMPORTANT
-----------------------------------
- ALWAYS use the tool
- NEVER hallucinate OID mappings
"""
    )