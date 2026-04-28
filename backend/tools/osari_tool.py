# tools/osari_tool.py

from langchain.tools import tool
from services.osari_service import get_mappings
from logger import get_logger

logger = get_logger(__name__)


@tool
def resolve_oids(conditions: list) -> list:
    """Resolve OIDs to mapping paths and entities"""

    logger.info("Resolving OIDs")

    mappings = get_mappings()

    enriched = []

    for c in conditions:
        mapping = next(
            (m for m in mappings if m["objectId"] == c["oid"]), None
        )

        enriched.append({
            **c,
            "path": mapping["path"] if mapping else None,
            "entity": mapping["entity"] if mapping else None
        })

    return enriched