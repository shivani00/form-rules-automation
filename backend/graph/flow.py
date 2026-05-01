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
from utils.validator import extract_json, validate_js
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


# ---------------- RULE NODE ----------------
def rule_node(state: AutomationState):

    logger.info("Rule Node")

    result = rule_agent.invoke({
        "messages": [
            {"role": "user", "content": json.dumps(state["intent"])}
        ]
    })

    messages = result.get("messages", [])
    if not messages:
        raise ValueError("No response from agent")

    message = messages[-1]

    if isinstance(message.content, list):
        raw_output = " ".join(
            part.get("text", "") for part in message.content if isinstance(part, dict)
        )
    else:
        raw_output = message.content

    logger.info(f"Rule agent output: {raw_output}")

    try:
        parsed = extract_json(raw_output)
    except:
        logger.error("Rule agent parsing failed")
        parsed = {"resolved_conditions": []}

    state["resolved_conditions"] = parsed.get("resolved_conditions", [])

    return state


# ---------------- LOGIC NODE ----------------
def logic_node(state):

    logger.info("Logic Node")

    intent = state["intent"]

    result = logic_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": json.dumps({
                    "conditions": state.get("resolved_conditions", []),
                    "states": intent.get("states", []),
                    "effective_date": intent.get("effective_date"),
                    "transactions": intent.get("transactions", [])
                })
            }
        ]
    })

    messages = result.get("messages", [])
    if not messages:
        raise ValueError("No response from agent")

    message = messages[-1]

    if isinstance(message.content, list):
        raw_output = " ".join(
            part.get("text", "") for part in message.content if isinstance(part, dict)
        )
    else:
        raw_output = message.content

    logger.info(f"Logic agent output: {raw_output}")

    try:
        parsed = extract_json(raw_output)
    except:
        parsed = {"logic": "AND", "rules": []}

    state["logic"] = parsed

    return state


# ---------------- HELPER NODE ----------------
def helper_node(state):

    logger.info("Helper Node")

    intent = state["intent"]
    logic = state["logic"]

    helpers = fetch_helpers.invoke({
        "workstream": intent.get("workstream", "wc"),
        "form_type": intent.get("form_type", "text")
    })

    result = helper_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": json.dumps({
                    "logic": logic,
                    "helpers": helpers
                })
            }
        ]
    })

    messages = result.get("messages", [])
    if not messages:
        raise ValueError("No response from agent")

    message = messages[-1]

    if isinstance(message.content, list):
        raw_output = " ".join(
            part.get("text", "") for part in message.content if isinstance(part, dict)
        )
    else:
        raw_output = message.content

    try:
        parsed = extract_json(raw_output)
        expressions = parsed.get("expressions", [])
    except:
        expressions = []

    if not expressions:
        logger.warning("No helper expressions found, falling back to logic paths")

    state["helper_expressions"] = expressions

    return state


# ---------------- CODEGEN NODE ----------------
def codegen_node(state):

    logger.info("Codegen Node")

    intent = state["intent"]
    logic = state["logic"]

    query = build_query_from_logic(logic)

    examples = retrieve_examples(
        workstream=intent.get("workstream", "wc"),
        query=query
    ) if logic.get("rules") else []

    feedback = ""

    for i in range(2):

        result = codegen_agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps({
                        "intent": intent,
                        "logic": logic,
                        "repo_examples": examples,
                        "helper_expressions": state.get("helper_expressions", []),
                        "patterns": RULE_PATTERNS,
                        "feedback": feedback
                    })
                }
            ]
        })

        messages = result.get("messages", [])
        if not messages:
            raise ValueError("No response from agent")

        message = messages[-1]

        if isinstance(message.content, list):
            raw_output = " ".join(
                part.get("text", "") for part in message.content if isinstance(part, dict)
            )
        else:
            raw_output = message.content

        try:
            parsed = extract_json(raw_output)
            code = parsed.get("code", "")
        except:
            parsed = {}
            code = ""

        errors = validate_template(code)

        if not errors:
            break

        feedback = f"Fix these issues: {errors}"

    state["generated_code"] = parsed.get("code", "")
    state["file_path"] = parsed.get("file_path", "")
    state["validation"] = validate_js(state["generated_code"])
    state["test_code"] = parsed.get("test_code", "")         
    state["test_file_path"] = parsed.get("test_file_path", "") 

    return state


# ---------------- DIFF NODE ----------------
def diff_node(state: AutomationState):

    logger.info("Diff Node")

    new_code = state["generated_code"].split("\n")

    diff_lines = [{"type": "added", "content": line} for line in new_code]

    state["diff"] = {
        "file_path": state["file_path"],
        "changes": diff_lines
    }

    return state


# ---------------- GRAPH ----------------
def build_graph():

    builder = StateGraph(AutomationState)

    builder.add_node("rule_node", rule_node)
    builder.add_node("logic_node", logic_node)
    builder.add_node("helper_node", helper_node)
    builder.add_node("codegen_node", codegen_node)
    builder.add_node("diff_node", diff_node)

    builder.set_entry_point("rule_node")

    builder.add_edge("rule_node", "logic_node")
    builder.add_edge("logic_node", "helper_node")
    builder.add_edge("helper_node", "codegen_node")
    builder.add_edge("codegen_node", "diff_node")
    builder.add_edge("diff_node", END)

    return builder.compile()


# ---------------- VALIDATOR ----------------
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