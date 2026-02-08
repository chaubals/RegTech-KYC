from dataclasses import dataclass

@dataclass
class RegulatoryRuleResult:
  rule_id:str
  description: str
  severity: str # low, medium, high