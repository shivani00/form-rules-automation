# agents/codegen_agent.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
# create_openai_tools_agent, 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.llm import get_llm
from tools.github_tool import (
    fetch_template,
    prepare_file_path,
)
from logger import get_logger

logger = get_logger(__name__)


def get_codegen_agent():

    llm = get_llm()

    tools = [
        fetch_template,
        prepare_file_path
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a JavaScript Rule Compiler.

You MUST generate code from structured logic.

-----------------------------------
INPUT
-----------------------------------
You receive:
- intent
- logic (structured rules)
- repo_examples (code snippets)
- helper_expressions (generated helper calls)
- patterns (code patterns from repo)

-----------------------------------
STEP 0 (MANDATORY)
-----------------------------------
Call:
fetch_template(workstream, form_type)
         
You MUST call fetch_template FIRST before generating code.

-----------------------------------
STEP 1: UNDERSTAND EXPRESSIONS
-----------------------------------

You will receive helper_expressions which already represent the logic.
Do NOT re-interpret logic rules.

-----------------------------------
STEP 2: USE HELPER EXPRESSIONS
-----------------------------------

You will receive:
- helper_expressions

These are already generated helper calls.

Example:
[
  "hasCoverage(data, '1234')",
  "(hasStateCd(data, 'MI') || hasStateCd(data, 'RI'))"
]

You MUST:
- Use these expressions directly
- DO NOT modify them
- DO NOT generate new helper calls
- DO NOT assume helper names
         
If helper_expressions is empty:
- Use logic.path to access data
- Example:
  data.policy.coverages.some(c => c.code === "<value>")

-----------------------------------
STEP 3: COMBINE EXPRESSIONS
-----------------------------------

- Combine helper_expressions using AND (&&)
- Expressions may already contain OR (||)
- Wrap final condition inside:

if (<combined_condition>) {
  isRuleFired = true;
}

-----------------------------------------------
STEP 4: USE REPO EXAMPLES 
-----------------------------------------------

Use patterns from repo_examples:
- how helpers are used
- how conditions grouped
- If repo_examples are empty, rely on patterns only.

If a helper is not known:
- Use path from logic to build condition directly from data
- Example:
  data.policy.coverages.some(c => c.code === "XYZ")
- DO NOT invent helper functions.

-----------------------------------
REFERENCE PATTERNS (FROM INPUT)
-----------------------------------
Use the provided patterns from input to guide:
- grouping
- helper usage

Use these patterns strictly (provided in input).
Follow structure and grouping.

-----------------------------------
STEP 5: GENERATE FINAL JS
-----------------------------------
Replace "// Code Logic" with FULL condition logic including:
- if statement
- isRuleFired assignment

-----------------------------------
RULE NUMBER EXTRACTION (MANDATORY)
-----------------------------------
Use intent.rule_number for file naming.
Do NOT use form_number.
Rule number MUST NOT contain parentheses.

Example:
WA12002233(00) → WA12002233

-----------------------------------
STEP 6 (MANDATORY)
-----------------------------------
Call:
prepare_file_path(workstream, rule_number, form_type)

-----------------------------------
OUTPUT
-----------------------------------

{{
  "code": "...",
  "file_path": "..."
}}

-----------------------------------
GUIDELINES
-----------------------------------
You MUST:
- Fill all placeholders
- If any placeholder remains, it is considered FAILURE.
- Generate unique IDs
- Populate notes section
- Replace ALL placeholders
- Return FULL JS code, not just the logic.
         
-----------------------------------
FEEDBACK (IMPORTANT)
-----------------------------------
If feedback is provided:
- Fix the issues strictly
- Do not repeat previous mistakes
"""),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    # agent = create_openai_tools_agent(llm, tools, prompt)
    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )