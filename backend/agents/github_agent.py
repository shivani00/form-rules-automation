from langchain.agents import create_agent
from core.llm import get_llm
from logger import get_logger

logger = get_logger(__name__)


def get_github_agent():
    llm = get_llm()

    return create_agent(
        model=llm,
        tools=[],
        system_prompt="""
You are a Git Assistant.

-----------------------------------
TASK
-----------------------------------
Generate a diff preview between:
- new file content
- empty file

-----------------------------------
OUTPUT
-----------------------------------
Return a readable unified diff format.

Example:

+ added line
- removed line

-----------------------------------
IMPORTANT
-----------------------------------
- Do NOT explain anything
- Return ONLY diff output
"""
    )