# routes/automation.py

from fastapi import APIRouter
from utils.validator import extract_json
from services.github_service import commit_file, create_branch, create_pr
from graph.flow import build_graph
from logger import get_logger
from memory.session_store import get_session, update_session, clear_session
from agents.edit_agent import get_edit_agent
from memory.conversation_memory import get_memory, clear_memory

logger = get_logger(__name__)

router = APIRouter(prefix="/automation")

graph = build_graph()

@router.post("/generate")
def generate(payload: dict):

    logger.info("Automation started")

    session_id = payload.get("session_id", "default")

    result = graph.invoke({
        "intent": payload["intent"]
    })

    # 🔥 store in session
    update_session(session_id, {
        "intent": payload["intent"],
        "logic": result.get("logic"),
        "helper_expressions": result.get("helper_expressions"),
        "code": result.get("generated_code"),
        "test_code": result.get("test_code"),
        "file_path": result.get("file_path"),
        "test_file_path": result.get("test_file_path")
    })

    return {
        "code": result["generated_code"],
        "file_path": result["file_path"],
        "test_code": result.get("test_code"),
        "test_file_path": result.get("test_file_path"),
        "diff": result.get("diff")
    }

@router.post("/create-pr")
def create_pr_route(payload: dict):

    logger.info("Creating PR")

    intent = payload["intent"]
    code = payload.get("code")
    test_code = payload.get("test_code")

    file_path = payload.get("file_path")
    test_file_path = payload.get("test_file_path")

    rule_number = intent.get("rule_number")

    # 🔴 HARD SAFETY CHECK
    if not code or len(code.strip()) < 20:
        logger.error("❌ EMPTY OR INVALID CODE RECEIVED")
        return {
            "message": "Code generation failed. No code to commit.",
            "error": "Empty code"
        }

    # 🔥 fallback ONLY if missing
    if not file_path:
        form_number_raw = intent["form_number"]
        form_number = form_number_raw.replace("(", "").replace(")", "")

        safe_rule = rule_number.replace(" ", "-")
        safe_form = form_number.replace(" ", "-")

        workstream = intent.get("workstream", "wc").lower()
        form_type = intent.get("form_type", "text").lower()

        folder = "fillin-forms" if form_type == "fillin" else "text-forms"

        file_name = safe_rule
        file_path = f"forms-{workstream}/{folder}/{file_name}.js"
        test_file_path = f"forms-{workstream}/{folder}/{file_name}.test.ts"

        branch = f"feature/{safe_rule}-{safe_form}"
    else:
        safe_rule = rule_number.replace(" ", "-")
        safe_form = intent["form_number"].replace(" ", "-")
        branch = f"feature/{safe_rule}-{safe_form}"

    logger.info(f"Branch: {branch}")
    logger.info(f"Rule file: {file_path}")
    logger.info(f"Test file: {test_file_path}")

    try:
        create_branch(branch)

        # ✅ commit rule file
        commit_file(branch, file_path, code)

        # ✅ commit test file
        if test_code and len(test_code.strip()) > 20:
            commit_file(branch, test_file_path, test_code)
        else:
            logger.warning("⚠️ No valid test_code provided")

        pr_url = create_pr(branch)

        return {
            "message": "PR Created",
            "pr_url": pr_url
        }

    except Exception as e:
        logger.error(f"PR creation failed: {str(e)}")
        return {
            "message": "PR creation failed",
            "error": str(e)
        }

edit_agent = get_edit_agent()


@router.post("/make-changes")
def make_changes(payload: dict):

    logger.info("Make changes triggered")

    session_id = payload.get("session_id", "default")
    instruction = payload.get("instruction")

    if not instruction:
        return {"error": "Instruction is required"}

    session = get_session(session_id)
    memory = get_memory(session_id)

    code = session.get("code")
    test_code = session.get("test_code")

    if not code:
        return {"error": "No code found in session"}

    # 🔥 add user message
    memory.add_user_message(instruction)

    # 🔥 format chat history properly
    chat_text = "\n".join([
        f"{m.type}: {m.content}" for m in memory.messages
    ])

    result = edit_agent.invoke({
        "messages": [
            {
                "role": "system",
                "content": f"Chat History:\n{chat_text}"
            },
            {
                "role": "user",
                "content": f"""
User Instruction:
{instruction}

Intent:
{session.get("intent")}

Logic:
{session.get("logic")}

Helper Expressions:
{session.get("helper_expressions")}

Existing Code:
{code}

Existing Test Code:
{test_code}
"""
            }
        ]
    })

    messages = result.get("messages", [])

    raw_output = ""
    if messages:
        last = messages[-1].content
        if isinstance(last, list):
            raw_output = " ".join(
                part.get("text", "") for part in last if isinstance(part, dict)
            )
        else:
            raw_output = last

    parsed = extract_json(raw_output)

    updated_code = parsed.get("code", code)
    updated_test_code = parsed.get("test_code", test_code)

    # 🔥 safety fallback
    if "module.exports" not in updated_code:
        logger.warning("Invalid edit detected, reverting code")
        updated_code = code

    if updated_test_code and "describe(" not in updated_test_code:
        logger.warning("Invalid test edit, reverting test")
        updated_test_code = test_code

    # 🔥 update session
    update_session(session_id, {
        "code": updated_code,
        "test_code": updated_test_code
    })

    # 🔥 store AI response in memory
    memory.add_ai_message(updated_code[:500])

    return {
        "code": updated_code,
        "test_code": updated_test_code
    }

@router.post("/reset-session")
def reset_session(payload: dict):

    session_id = payload.get("session_id", "default")

    clear_session(session_id)
    clear_memory(session_id)

    return {"message": "Session reset successful"}