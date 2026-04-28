# services/repo_retriever.py

import os
from logger import get_logger

logger = get_logger(__name__)

BASE_DIR = "repo_clone"  # your local repo copy


def load_files(workstream: str):
    """Load only relevant files (scoped retrieval)"""

    files = []

    base_path = os.path.join(BASE_DIR, f"forms-{workstream}")

    for root, _, filenames in os.walk(base_path):
        for f in filenames:
            if f.endswith(".js"):
                try:
                    with open(os.path.join(root, f), "r") as file:
                        content = file.read()

                        files.append({
                            "path": os.path.join(root, f),
                            "content": content
                        })
                except:
                    continue

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