from fastapi import APIRouter
from agents.jira_agent import get_jira_agent
from services.jira_service import save_jira_result, get_all_jira
from logger import get_logger
from utils.validator import extract_json


logger = get_logger(__name__)

router = APIRouter(prefix="/ai")

jira_agent = get_jira_agent()


def normalize_rule(rule_number: str):
    if not rule_number:
        return None
    return rule_number.split("(")[0]


@router.post("/analyze-jira")
def analyze_jira(payload: dict):

    jira_url = payload.get("jira_url")

    if not jira_url:
        return {"error": "jira_url is required"}

    result = jira_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
Process Jira story: {jira_url}

IMPORTANT:
- Identify RULE NUMBER vs FORM NUMBER correctly
- WC is workstream, not transaction
- Extract OID conditions
"""
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

    logger.info(f"Jira agent raw output: {raw_output}")

    output = extract_json(raw_output)

    saved = save_jira_result(jira_url, output)

    return saved


@router.get("/jira-rules")
def get_rule_list():
    data = get_all_jira()

    rules = [
        {
            "rule_number": r.get("rule_number"),
            "form_number": r.get("form_number"),
            "story_count": len(r.get("stories", []))
        }
        for r in data
    ]

    # sort latest first
    rules = sorted(rules, key=lambda x: x["rule_number"], reverse=True)

    logger.info(f"Returning {len(rules)} rules")

    return rules


@router.get("/jira-by-rule/{rule_number}")
def get_jira_by_rule(rule_number: str):

    rule_number = normalize_rule(rule_number)

    logger.info(f"Fetching Jira stories for rule: {rule_number}")

    data = get_all_jira()

    match = next(
        (r for r in data if r.get("rule_number") == rule_number),
        None
    )

    if not match:
        return {"message": "No Jira found"}

    stories = sorted(
        match.get("stories", []),
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    return {
        "rule_number": match.get("rule_number"),
        "form_number": match.get("form_number"),
        "stories": stories
    }