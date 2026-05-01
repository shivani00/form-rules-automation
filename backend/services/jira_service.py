import json
import os
from uuid import uuid4
from config import config
from logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

FILE_PATH = config.JIRA_FILE


def read_data():
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as f:
        return json.load(f)


def write_data(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def normalize_rule(rule_number: str):
    """
    Convert:
    WASDR123(00) → WASDR12300
    """
    if not rule_number:
        return None

    return rule_number.replace("(", "").replace(")", "").strip()


def normalize_url(url: str):
    """Normalize Jira URL (remove trailing slash, lowercase)"""
    if not url:
        return None
    return url.strip().rstrip("/").lower()


def save_jira_result(jira_url, intent):
    data = read_data()

    raw_rule_number = intent.get("rule_number")
    rule_number = normalize_rule(raw_rule_number)

    if not rule_number:
        logger.error("Missing rule_number in intent. Skipping save.")
        return {"error": "rule_number missing"}

    jira_url_normalized = normalize_url(jira_url)

    logger.info(f"Saving Jira for rule: {rule_number}")

    existing = next(
        (item for item in data if item.get("rule_number") == rule_number),
        None
    )

    story = {
        "id": str(uuid4()),
        "jira_url": jira_url,
        "created_at": datetime.utcnow().isoformat()
    }

    if existing:
        logger.info(f"Checking duplicates for rule: {rule_number}")

        existing_stories = existing.get("stories", [])

        already_exists = any(
            normalize_url(s.get("jira_url")) == jira_url_normalized
            for s in existing_stories
        )

        if already_exists:
            logger.info(f"Duplicate Jira found. Skipping save for: {jira_url}")

            return {
                "intent": intent,
                "story_id": None
            }

        logger.info(f"Appending new Jira story to rule: {rule_number}")

        existing.setdefault("stories", []).append(story)

        existing["form_number"] = intent.get("form_number")
        existing["workstream"] = intent.get("workstream")

    else:
        logger.info(f"Creating new rule entry: {rule_number}")

        entry = {
            "rule_number": rule_number,
            "form_number": intent.get("form_number"),
            "workstream": intent.get("workstream"),
            "stories": [story]
        }

        data.append(entry)

    write_data(data)

    return {
        "intent": intent,
        "story_id": story["id"]
    }

def get_all_jira():
    return read_data()