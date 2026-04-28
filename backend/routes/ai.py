from fastapi import APIRouter
from agents.jira_agent import get_jira_agent
from services.jira_service import save_jira_result, get_all_jira
from logger import get_logger
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/ai")

jira_agent = get_jira_agent()


@router.post("/analyze-jira")
def analyze_jira(payload: dict):
    jira_url = payload.get("jira_url")

    result = jira_agent.invoke({
    "input": f"""
Process Jira story: {jira_url}

IMPORTANT:
- Identify RULE NUMBER vs FORM NUMBER correctly
- WC is workstream, not transaction
- Extract OID conditions
"""
})

    output = result.get("output", {})

    if isinstance(output, str):
        try:
            output = json.loads(output)
        except:
            output = {"raw": output}

    # 🔥 SAVE HISTORY
    saved = save_jira_result(jira_url, output)

    return saved


@router.get("/jira-history")
def get_history():
    return get_all_jira()