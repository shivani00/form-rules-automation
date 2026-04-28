# utils/js_validator.py

from logger import get_logger

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