from app.graph.state import KYCState
from app.rules.us import apply_us_kyc_rules

def regulatory_rules_agent(state: KYCState) -> KYCState:
  country = state.get("user_metadata", {}).get("country", "US")

  rule_results = []

  if country == "US":
    rule_results = apply_us_kyc_rules(state)
  else:
    # Future consideration: add other jurisdictions
    rule_results = []

  regulatory_flags = []
  regulatory_analysis = []

  for result in rule_results:
    regulatory_flags.append(result.rule_id)
    regulatory_analysis.append({
      "rule_id": result.rule_id,
      "description": result.description,
      "severity": result.severity
    })

  # EDD logic (explicit)
  edd_required = any(
    r.severity == "high" for r in rule_results
  )

  if edd_required:
    regulatory_flags.append("EDD_REQUIRED")

  state["regulatory_flags"] = regulatory_flags
  state["regulatory_analysis"] = regulatory_analysis

  state["audit_log"].append({
    "agent": "regulatory_rules",
    "country": country,
    "rules_triggered": regulatory_flags
  })

  return state
