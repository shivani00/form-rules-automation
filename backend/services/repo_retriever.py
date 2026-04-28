# services/repo_retriever.py

import base64
from config import config
from logger import get_logger
from typing import List, Dict
from github import Github

logger = get_logger(__name__)

g = Github(config.GITHUB_TOKEN)
repo = g.get_repo(config.GITHUB_REPO)

def load_files(
    workstream: str,
    form_type: str = "text",
    include_helpers: bool = False
) -> List[Dict]:
    """
    Load JS files directly from GitHub repo.

    Args:
        workstream: wc, auto, etc.
        form_type: text / fillin
        include_helpers: include helper files or not

    Returns:
        List of {path, content}
    """

    files: List[Dict] = []

    folder = "fillin-forms" if form_type.lower() == "fillin" else "text-forms"

    base_path = f"forms-{workstream.lower()}/{folder}"

    try:
        contents = repo.get_contents(base_path, ref=config.GITHUB_BASE_BRANCH)
    except Exception as e:
        logger.error(f"Failed to fetch repo contents: {e}")
        return files

    def walk(contents_list):
        for item in contents_list:

            # 🔥 skip .config unless helpers needed
            if not include_helpers and ".config" in item.path:
                continue

            if item.type == "dir":
                try:
                    walk(repo.get_contents(item.path, ref=config.GITHUB_BASE_BRANCH))
                except Exception as e:
                    logger.error(f"Error reading dir {item.path}: {e}")

            elif item.path.endswith(".js"):
                try:
                    content = base64.b64decode(item.content).decode()

                    files.append({
                        "path": item.path,
                        "content": content
                    })

                except Exception as e:
                    logger.error(f"Error reading file {item.path}: {e}")

    walk(contents)

    logger.info(f"Loaded {len(files)} files from GitHub path: {base_path}")

    return files


def simple_score(content: str, query: str):
    """Basic keyword scoring"""

    score = 0
    for q in query.lower().split():
        if q in content.lower():
            score += 1
    return score


def retrieve_examples(workstream: str, query: str, top_k: int = 3):

    files = load_files(workstream)

    scored = []

    for f in files:
        score = simple_score(f["content"], query)
        if score > 0:
            scored.append((score, f))

    scored.sort(reverse=True, key=lambda x: x[0])

    top_files = [f for _, f in scored[:top_k]]

    return [
        {
            "path": f["path"],
            "snippet": f["content"][:1500]  # limit tokens
        }
        for f in top_files
    ]