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
        "diff": result["diff"],
        "validation": result.get("validation")  # optional but useful
    }


@router.post("/create-pr")
def create_pr_route(payload: dict):

    logger.info("Creating PR")

    intent = payload["intent"]
    code = payload["code"]

    # 🔥 NEW NAMING LOGIC
    rule_number = intent.get("rule_number")
    form_number_raw = intent["form_number"]

    # clean values
    form_number = form_number_raw.replace("(", "").replace(")", "")
    safe_rule = rule_number.replace(" ", "-")
    safe_form = form_number.replace(" ", "-")

    # ✅ FILE NAME = RULE TYPE
    file_name = safe_rule

    # ✅ BRANCH NAME = RULE + FORM
    branch = f"feature/{safe_rule}-{safe_form}"

    # 🔥 ADD BACK THESE (MISSING)
    workstream = intent.get("workstream", "wc").lower()
    form_type = intent.get("form_type", "text").lower()

    folder = "fillin-forms" if form_type == "fillin" else "text-forms"

    # ✅ FINAL PATH
    file_path = f"forms-{workstream}/{folder}/{file_name}.js"

    logger.info(f"Branch: {branch}")
    logger.info(f"File path: {file_path}")

    try:
        create_branch(branch)
        commit_file(branch, file_path, code)
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