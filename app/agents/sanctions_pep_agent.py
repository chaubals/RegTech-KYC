from app.graph.state import KYCState
from app.services.mock_sanctions_data import SANCTIONS_LIST, PEP_LIST
from app.utils.name_matching import similarity
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
  model="gpt-4o",
  temperature=0,
)

SIMILARITY_THRESHOLD = 0.85

SANCTIONS_SCHEMA = {
  "type": "object",
  "properties": {
    "sanctions_match": {"type": "boolean"},
    "pep_match": {"type": "boolean"},
    "risk_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "matched_names": {
      "type": "array",
      "items": {"type": "string"}
    },
    "analysis_summary": {"type": "string"}
  },
  "required": [
    "sanctions_match",
    "pep_match",
    "risk_score",
    "matched_names",
    "analysis_summary"
  ]
}

def sanctions_pep_screening_agent(state: KYCState) -> KYCState:
  documents = state.get("extracted_data", {}).get("documents", [])
  if not documents:
    return state
  
  # Pick the document with highest confidence
  primary_doc = max(documents, key=lambda d: d.get("confidence", 0))
  full_name = primary_doc["fields"].get("full_name")

  if not full_name:
    return state

  potential_matches = []

  for entry in SANCTIONS_LIST + PEP_LIST:
    score = similarity(full_name, entry["name"])
    if score >= SIMILARITY_THRESHOLD:
      potential_matches.append({
        "name": entry["name"],
        "type": entry["type"],
        "score": score
      })

  # If no matches, return clean report
  if not potential_matches:
    state["sanctions_report"] = {
      "sanctions_match": False,
      "pep_match": False,
      "risk_score": 0.0,
      "matched_names": [],
      "analysis_summary": "No matches found against sanctions or PEP lists."
    }

    return state

  # Use gpt-4o to reason about false positives
  analysis = analyze_matches_with_gpt(full_name, potential_matches)

  state["sanctions_report"] = analysis

  state["audit_log"].append({
    "agent": "sanctions_pep_screening",
    "screened_name": full_name,
    "potential_matches": potential_matches
  })

  return state

def analyze_matches_with_gpt(subject_name: str, matches: list) -> dict:
  system_prompt = (
    "You are a sanctions and PEP (politically exposed person) analyst. \n"
    "Assess whether name matches are likely true matches or false positives. \n"
    "Be conservative and explain your reasoning."
  )

  user_prompt = f"""
  Customer name: {subject_name}

  Potential matches:
  {matches}

  Determine:
  - sanctions_match (true/false)
  - pep_match (true/false)
  - overall risk_score (0 to 1)
  - matched_names (only meaningful matches)
  """

  response = llm.invoke(
    [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ],
    response_format={
      "type": "json_schema",
      "json_schema": SANCTIONS_SCHEMA
    }
  )

  return response.content