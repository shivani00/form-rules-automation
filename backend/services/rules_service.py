import json
import os
from uuid import uuid4
from config import config
from logger import get_logger

logger = get_logger("rule_service")


def read_rules():
    logger.info("Reading rules from file")

    if not os.path.exists(config.DATA_FILE):
        logger.warning("Rules file not found, returning empty list")
        return []

    with open(config.DATA_FILE, "r") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} rules")
    return data


def write_rules(data):
    logger.info(f"Writing {len(data)} rules to file")

    with open(config.DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_rule(rule_dict):
    logger.info("Creating new rule")

    rules = read_rules()
    rule_dict["id"] = str(uuid4())

    rules.append(rule_dict)
    write_rules(rules)

    logger.info(f"Rule created with ID: {rule_dict['id']}")
    return rule_dict


def update_rule(rule_id, updated_rule):
    logger.info(f"Updating rule: {rule_id}")

    rules = read_rules()

    for i, r in enumerate(rules):
        if r["id"] == rule_id:
            updated_rule["id"] = rule_id
            rules[i] = updated_rule
            write_rules(rules)

            logger.info("Rule updated successfully")
            return updated_rule

    logger.error("Rule not found for update")
    return None


def delete_rule(rule_id):
    logger.info(f"Deleting rule: {rule_id}")

    rules = read_rules()
    new_rules = [r for r in rules if r["id"] != rule_id]

    write_rules(new_rules)

    logger.info("Rule deleted")
    return {"message": "Deleted"}


def get_all_rules():
    logger.info("Fetching all rules")
    return read_rules()