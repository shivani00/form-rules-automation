import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(BASE_DIR, "storage", "rules.json")
    OSARI_FILE = os.path.join(BASE_DIR, "storage", "osari.json")
    JIRA_FILE = os.path.join(BASE_DIR, "storage", "jira_history.json")

    LOG_LEVEL = "INFO"
    APP_NAME = "AI Rule Backend"

    # 🔥 JIRA CONFIG
    JIRA_BASE_URL = "https://formslibrary.atlassian.net"
    JIRA_EMAIL = "gupta.shivani1296@gmail.com"
    JIRA_API_TOKEN = ""

    GITHUB_TOKEN = ""
    GITHUB_REPO = "shivani00/forms-repo"
    GITHUB_BASE_BRANCH = "main"

    GOOGLE_API_KEY = ""

config = Config()

