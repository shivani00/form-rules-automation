import json
import os
from uuid import uuid4
from config import config
from logger import get_logger

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


def save_jira_result(jira_url, intent):
    data = read_data()

    entry = {
        "id": str(uuid4()),
        "jira_url": jira_url,
        "intent": intent
    }

    data.append(entry)
    write_data(data)

    return entry


def get_all_jira():
    return read_data()