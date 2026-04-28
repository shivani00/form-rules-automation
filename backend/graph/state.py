# graph/state.py

from typing import TypedDict, List, Dict, Any

class AutomationState(TypedDict):
    intent: Dict[str, Any]
    resolved_conditions: List[Dict]
    logic: Dict
    template: str
    generated_code: str
    file_path: str
    diff: str
    pr_url: str
    helper_expressions: List[Dict]