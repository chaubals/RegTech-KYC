from app.rules.base import RegulatoryRuleResult

def apply_us_kyc_rules(state) -> list[RegulatoryRuleResult]:
  results = []

  consistency = state.get(f"consistency_report", {})
  documents = state.get("extracted_data", {}).get("documents", [])

  # Rule 1: Expired documents
  if consistency.get("expired_documents"):
    results.append(
      RegulatoryRuleResult(
        rule_id="US-KYC-001",
        description="Expired identity document detected",
        severity="high"
      )
    )

  # Rule 2: Name mismatch
  if not consistency.get("name_match", True):
    results.append(
      RegulatoryRuleResult(
        rule_id="US-KYC-002",
        description="Name mismatch identified across submitted documents",
        severity="high"
      )
    )

  # Rule 3: Address mismatch
  if not consistency.get("address_match", True):
    results.append(
      RegulatoryRuleResult(
        rule_id="US-KYC-003",
        description="Address mismatch identified across documents",
        severity="medium"
      )
    )

  # Rule 4: Missing expiry date on ID
  for doc in documents:
    if doc["document_type"] in ["passport", "driving_license"]:
      if not doc["fields"].get("expiry_date"):
        results.append(
          RegulatoryRuleResult(
            rule_id="US-KYC-004",
            description=f"Missing expiry date on ID: {doc['document_type']}",
            severity="medium"
          )
        )

  return results