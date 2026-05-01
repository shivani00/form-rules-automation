# routes/automation.py

from fastapi import APIRouter
from services.github_service import commit_file, create_branch, create_pr
from graph.flow import build_graph
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/automation")

graph = build_graph()

@router.post("/generate")
def generate(payload: dict):

    logger.info("Automation started")

    result = graph.invoke({
        "intent": payload["intent"]
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