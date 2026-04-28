import requests
from requests.auth import HTTPBasicAuth
from langchain.tools import tool
from config import config
from logger import get_logger

logger = get_logger(__name__)


@tool
def fetch_jira_story(jira_url: str) -> str:
    """
    Fetch Jira story description using Jira API
    """

    logger.info(f"Fetching Jira story from URL: {jira_url}")

    try:
        # Extract issue key (e.g. STORY-5)
        issue_key = jira_url.rstrip("/").split("/")[-1]

        api_url = f"{config.JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(config.JIRA_EMAIL, config.JIRA_API_TOKEN),
            headers={"Accept": "application/json"}
        )

        if response.status_code != 200:
            logger.error(f"Jira API failed: {response.text}")
            return f"Error fetching Jira: {response.text}"

        data = response.json()

        fields = data.get("fields", {})

        summary = fields.get("summary", "")
        description = fields.get("description", "")

        # ⚠️ Jira description is nested → simplify
        def extract_text(node):
            texts = []

            if isinstance(node, dict):
                if "text" in node:
                    texts.append(node["text"])

                for key in node:
                    texts.extend(extract_text(node[key]))

            elif isinstance(node, list):
                for item in node:
                    texts.extend(extract_text(item))

            return texts

        desc_text = extract_text(description)

        full_text = f"""
        SUMMARY:
        {summary}

        DESCRIPTION:
        {desc_text}
        """

        logger.info("Jira story fetched successfully")

        return full_text

    except Exception as e:
        logger.error(f"Error fetching Jira: {str(e)}")
        return f"Error: {str(e)}"