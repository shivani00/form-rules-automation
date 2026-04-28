RULE_PATTERNS = [
  {
    "name": "coverage + state",
    "description": "Coverage condition combined with multiple states",
    "logic": "AND(coverage, OR(states))",
    "example": """
if (
  hasCoverage(data, "1234") &&
  (hasStateCd(data, "MI") || hasStateCd(data, "RI"))
) {
  isRuleFired = true;
}
"""
  },
  {
    "name": "coverage + date",
    "description": "Coverage with effective date",
    "logic": "AND(coverage, date>=)",
    "example": """
if (
  hasCoverage(data, "1234") &&
  isEffectiveDateOnOrAfter(data, "2026-01-01")
) {
  isRuleFired = true;
}
"""
  }
]