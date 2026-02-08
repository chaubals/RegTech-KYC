from typing import TypedDict, Optional, List, Dict

class KYCState(TypedDict):
  #Raw Inputs
  documents: List[Dict]
  user_metadata: Dict

  #Parsed outputs
  extracted_data: Dict

  #Checks
  consistency_report: Dict
  regulatory_flags: List[str]
  sanctions_report: Dict

  #Decisions
  decision: Optional[str]
  decision_reasoning: Optional[str]

  #Audit
  audit_log: List[Dict]
   