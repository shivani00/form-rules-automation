# tools/github_tool.py

from langchain.tools import tool
from services.repo_retriever import load_files
from github import Github
from config import config
from logger import get_logger
import base64
import re

logger = get_logger(__name__)

g = Github(config.GITHUB_TOKEN)
repo = g.get_repo(config.GITHUB_REPO)


@tool
def fetch_template(workstream: str, form_type: str = "text") -> str:
    """
    Fetch the template.js file from the GitHub repository.

    Args:
        workstream (str): Business workstream (e.g., "wc", "auto").
        form_type (str): Type of form ("text" or "fillin"). Defaults to "text".

    Behavior:
        - Determines correct folder based on form_type
        - Constructs path dynamically
        - Fetches template.js from .config directory

    Returns:
        str: Decoded JavaScript template content

    Raises:
        Exception: If template file is not found in the repo
    """

    logger.info(f"Fetching template for workstream={workstream}, form_type={form_type}")

    folder = "fillin-forms" if form_type.lower() == "fillin" else "text-forms"
    path = f"forms-{workstream.lower()}/{folder}/.config/template.js"

    logger.info(f"Resolved template path: {path}")

    try:
        file = repo.get_contents(path, ref=config.GITHUB_BASE_BRANCH)
    except Exception as e:
        logger.error(f"Template not found at path: {path}")
        raise e

    return base64.b64decode(file.content).decode()


@tool
def prepare_file_path(workstream: str, rule_number: str, form_type: str = "text") -> str:
    """
    Generate the final file path for a new rule file in the repository.

    Args:
        workstream (str): Business workstream (e.g., "wc", "auto")
        form_number (str): Form number (e.g., "WA12002233(00)")
        form_type (str): Form type ("text" or "fillin")

    Behavior:
        - Cleans special characters from form_number
        - Selects correct folder (text-forms or fillin-forms)
        - Builds full GitHub file path

    Returns:
        str: Final file path (e.g., forms-wc/text-forms/WA12002233.js)
    """

    folder = "fillin-forms" if form_type.lower() == "fillin" else "text-forms"

    clean_rule = rule_number.replace("(", "").replace(")", "")

    return f"forms-{workstream.lower()}/{folder}/{clean_rule}.js"


@tool
def fetch_helpers(workstream: str) -> list:
    """
    Fetch helper functions from repo and return metadata
    """
    files = load_files(workstream)  # reuse your repo loader

    helpers = []

    for f in files:
        if "module.exports" in f["content"] and "fn:" in f["content"] and "name:" in f["content"]:
            # extract name
            name_match = re.search(r'name:\s*"(\w+)"', f["content"])
            params_match = re.search(r'fn:\s*\((.*?)\)', f["content"])

            if name_match and params_match:
                params = [p.strip() for p in params_match.group(1).split(",")]

                helpers.append({
                    "name": name_match.group(1),
                    "params": params,
                    "source": f["path"]
                })

    return helpers
