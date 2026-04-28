from fastapi import APIRouter, HTTPException
from models import Rule
from services.rules_service import (
    create_rule,
    get_all_rules,
    update_rule,
    delete_rule
)
from logger import get_logger

logger = get_logger("rules_api")

router = APIRouter()


@router.post("/rules")
def add_rule(rule: Rule):
    logger.info("API CALL: Create Rule")
    created = create_rule(rule.dict())
    return created


@router.get("/rules")
def fetch_rules():
    logger.info("API CALL: Fetch Rules")
    return get_all_rules()


@router.put("/rules/{rule_id}")
def edit_rule(rule_id: str, rule: Rule):
    logger.info(f"API CALL: Update Rule {rule_id}")

    updated = update_rule(rule_id, rule.dict())

    if not updated:
        logger.error("Rule not found")
        raise HTTPException(status_code=404, detail="Rule not found")

    return updated


@router.delete("/rules/{rule_id}")
def remove_rule(rule_id: str):
    logger.info(f"API CALL: Delete Rule {rule_id}")
    return delete_rule(rule_id)