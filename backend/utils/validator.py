# utils/js_validator.py

from logger import get_logger
import json, re

logger = get_logger(__name__)


def validate_js(code: str):
    logger.info("Validating JS")

    errors = []

    if "module.exports" not in code:
        errors.append("Missing module.exports")

    if "function" not in code:
        errors.append("Missing function block")

    if "createNewFormsListItemXX" not in code:
        errors.append("No form creation logic found")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def validate_template(code):

    errors = []

    if "id" not in code:
        errors.append("Missing id")

    if "effectiveDate" not in code:
        errors.append("Missing effectiveDate")

    if "<" in code or ">" in code:
        errors.append("Unreplaced placeholders found")

    if "module.exports" not in code:
        errors.append("Invalid JS structure")

    if "createNewFormsListItem" not in code:
        errors.append("Missing form creation logic")

    return errors

def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {}