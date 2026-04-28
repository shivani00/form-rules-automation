# graph/flow.py

from langgraph.graph import StateGraph, END
from agents.logic_agent import get_logic_agent
from agents.helper_agent import get_helper_agent
from tools.github_tool import fetch_helpers
from patterns import RULE_PATTERNS
from graph.state import AutomationState
from agents.rule_agent import get_rule_agent
from agents.codegen_agent import get_codegen_agent
from agents.github_agent import get_github_agent
from utils.js_validator import validate_js
from logger import get_logger
from services.repo_retriever import retrieve_examples
from utils.query_builder import build_query_from_logic
import json

logger = get_logger(__name__)

rule_agent = get_rule_agent()
codegen_agent = get_codegen_agent()
github_agent = get_github_agent()
logic_agent = get_logic_agent()
helper_agent = get_helper_agent()


def rule_node(state: AutomationState):

    logger.info("Rule Node")

    result = rule_agent.invoke({
        "input": json.dumps(state["intent"])
    })

    raw_output = result.get("output")

    logger.info(f"Rule agent output: {raw_output}")

    try:
        if not raw_output:
            logger.error("Empty output from codegen agent")
            raise ValueError("LLM returned empty output")
        parsed = json.loads(raw_output)
    except:
        logger.error("Rule agent parsing failed")
        parsed = {"resolved_conditions": []}

    state["resolved_conditions"] = parsed.get("resolved_conditions", [])

    return state

def codegen_node(state):

    logger.info("Codegen Node")

    intent = state["intent"]
    logic = state["logic"]

    # 🔥 STEP 1: BUILD QUERY
    query = build_query_from_logic(logic)

    # 🔥 STEP 2: RETRIEVE CONTEXT
    examples = retrieve_examples(
        workstream=intent.get("workstream", "wc"),
        query=query
    ) if logic.get("rules") else []

    # 🔥 STEP 3: CALL AGENT
    feedback = ""
    for i in range(2):
        result = codegen_agent.invoke({
            "input": json.dumps({
                "intent": intent,
                "logic": logic,
                "helper_expressions": state.get("helper_expressions", []),
                "repo_examples": examples,
                "patterns": RULE_PATTERNS,
                "feedback": feedback
            })
        })

        raw_output = result.get("output")

        try:
            parsed = json.loads(raw_output)
            code = parsed.get("code", "")
        except:
            code = ""
            parsed = {}

        errors = validate_template(code)

        if not errors:
            break

        # 🔥 feedback loop
        feedback = f"Fix these issues: {errors}"

    code = parsed.get("code", "")
    file_path = parsed.get("file_path", "")

    validation = validate_js(code)

    state["generated_code"] = code
    state["file_path"] = file_path
    state["validation"] = validation

    return state

def helper_node(state):

    logger.info("Helper Node")

    intent = state["intent"]
    logic = state["logic"]

    helpers = fetch_helpers.run({
        "workstream": intent.get("workstream", "wc")
    })

    result = helper_agent.invoke({
        "input": json.dumps({
            "logic": logic,
            "helpers": helpers
        })
    })

    try:
        parsed = json.loads(result.get("output", "{}"))
    except:
        parsed = {"expressions": []}

    expressions = parsed.get("expressions", [])

    if not expressions:
        logger.warning("No helper expressions found, falling back to logic paths")

    state["helper_expressions"] = expressions

    return state

def diff_node(state: AutomationState):

    logger.info("Diff Node")

    new_code = state["generated_code"].split("\n")

    diff_lines = []

    for line in new_code:
        diff_lines.append({
            "type": "added",
            "content": line
        })

    state["diff"] = {
        "file_path": state["file_path"],
        "changes": diff_lines
    }

    return state

def logic_node(state):

    logger.info("Logic Node")

    intent = state["intent"]

    result = logic_agent.invoke({
        "input": json.dumps({
            "conditions": state.get("resolved_conditions", []),
            "states": intent.get("states", []),
            "effective_date": intent.get("effective_date"),
            "transactions": intent.get("transactions", [])
        })
    })

    raw_output = result.get("output")

    logger.info(f"Logic agent output: {raw_output}")

    try:
        parsed = json.loads(raw_output)
    except:
        parsed = {"logic": "AND", "rules": []}

    state["logic"] = parsed

    return state

def build_graph():

    builder = StateGraph(AutomationState)

    builder.add_node("rule_node", rule_node)
    builder.add_node("logic_node", logic_node)
    builder.add_node("codegen_node", codegen_node)
    builder.add_node("diff_node", diff_node)
    builder.add_node("helper_node", helper_node)

    builder.set_entry_point("rule_node")

    builder.add_edge("rule_node", "logic_node")
    builder.add_edge("logic_node", "helper_node")
    builder.add_edge("helper_node", "codegen_node")
    builder.add_edge("codegen_node", "diff_node")

    builder.add_edge("diff_node", END)

    return builder.compile()

def validate_template(code):

    errors = []

    if "id" not in code:
        errors.append("Missing id")

    if "effectiveDate" not in code:
        errors.append("Missing effectiveDate")

    if "<" in code or ">" in code:
        errors.append("Unreplaced placeholders found")

    if "module.exports" not in code:
        errors.append("Invalid JS structure")

    if "createNewFormsListItem" not in code:
        errors.append("Missing form creation logic")

    return errors