# agents/github_agent.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
# create_openai_tools_agent, 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.llm import get_llm
from logger import get_logger

logger = get_logger(__name__)


def get_github_agent():

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a Git Assistant.

Generate a diff preview between:
- new file content
- empty file

Return readable diff.
"""),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    # agent = create_openai_tools_agent(llm, [], prompt)
    agent = create_tool_calling_agent(llm, [], prompt)

    return AgentExecutor(agent=agent, tools=[], verbose=True, handle_parsing_errors=True)