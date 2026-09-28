from requests.utils import address_in_network
from app.graph.state import KYCState
from langchain_openai import ChatOpenAI
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
  model='gpt-4o',
  temperature=0,
)

CONSISTENCY_SCHEMA = {
  "type": "object",
  "properties": {
    "name_match": {"type": "boolean"},
    "dob_match": {"type": "boolean"},
    "address_match": {"type": "boolean"},
    "expired_documents": {"type": "boolean"},
    "mismatched_fields": {
      "type": "array",
      "items": {"type": "string"}
    },
    "analysis_summary": {"type": "string"},
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
    }
  },
  "required": [
    "name_match",
    "dob_match",
    "address_match",
    "expired_documents",
    "mismatched_fields",
    "analysis_summary",
    "confidence"
  ]
}

def cross_document_consistency_agent(state: KYCState) -> KYCState:
  documents = state.get("extracted_data", {}).get("documents", [])

  if len(documents) < 1:
    # Not enough documents to compare
    state["consistency_report"] = {
      "name_match": True,
      "dob_match": True,
      "address_match": True,
      "expired_documents": False,
      "mismatched_fields": [],
      "analysis_summary": "Only 1 documents provided. Not enough documents to compare.",
      "confidence": 1.0
    }

    return state

  # Pre-check for expired documents (deterministic)
  expired = False
  today = datetime.now(timezone.utc).date()

  for doc in documents:
    expiry = doc["fields"].get("expiry_date")
    if expiry:
      try:
        if datetime.strptime(expiry, "%Y-%m-%d").date() < today:
          expired = True
      except ValueError:
        pass

  consistency = analyze_with_gpt(documents, expired)

  state["consistency_report"] = consistency

  state["audit_log"].append({
    "agent": "cross_document_consistency",
    "status": "completed",
    "expired_documents": consistency["expired_documents"],
    "mismatches": consistency["mismatched_fields"]
  })

  return state


def analyze_with_gpt(documents: list, expired_documents: bool) -> dict:
  system_prompt = (
    "You are a KYC cross-document consistency analysis system. \n"
    "Compare identity fields across documents. \n"
    "Allow minor formatting differences (e.g. address abbrevations, punctuation marks, etc.), but the actual values must match across documents. \n"
    "Flag mismatches only when meaninfully inconsistent. \n"
    "Do NOT guess missing values. \n"
    "Explain your reasoning clearly"
  )

  user_prompt = f"""
  DOCUMENTS::
  {documents}

  Expired documents detected: {expired_documents}

  Analyze consistency across:
  - full_name
  - date_of_birth
  - address

  Return mismatches only if fields conflict across documents.
  """

  response = llm.invoke(
    [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ],
    response_format={
      "type": "json_schema",
      "json_schema": CONSISTENCY_SCHEMA
    }
  )

  return response.content