from app.graph.state import KYCState
from langchain_openai import ChatOpenAI
from pdf2image import convert_from_path
import easyocr
import uuid
import os
from dotenv import load_dotenv


load_dotenv()

llm = ChatOpenAI(
  model='gpt-4o', 
  temperature=0,
)

reader = easyocr.Reader(['en'], gpu=False)

DOCUMENT_SCHEMA = {
  "type": "object",
  "properties": {
    "document_type": {
      "type": "string",
      "enum": ["passport", "driving_license", "national_id", "id_card", "unknown"]
    },
    "full_name": {"type": ["string", "null"]},
    "date_of_birth": {"type": ["string", "null"]},
    "address": {"type": ["string", "null"]},
    "expiry_date": {"type": ["string", "null"]},
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    }
  },
  "required": [
    "document_type",
    "full_name",
    "date_of_birth",
    "address",
    "expiry_date",
    "confidence"
  ]
}

def document_parsing_agent(state: KYCState) -> KYCState:
  extracted_documents = []

  for doc in state.get("documents", []):
    doc_path = doc.get("path")
    if not doc_path:
      continue

    document_id = str(uuid.uuid4())

    try:
      images = convert_from_path(doc_path)
      raw_text = ""

      for image in images:
        ocr_results = reader.readtext(image)
        raw_text += " ".join([r[1] for r in ocr_results]) + "\n"

      extraction = extract_fields_with_gpt(raw_text)

      extracted_documents.append({
                "document_id": document_id,
                "document_type": extraction["document_type"],
                "fields": {
                    "full_name": extraction["full_name"],
                    "date_of_birth": extraction["date_of_birth"],
                    "address": extraction["address"],
                    "expiry_date": extraction["expiry_date"],
                },
                "confidence": extraction["confidence"]
            })
      state["audit_log"].append({
        "agent": "document_parsing",
        "document_id": document_id,
        "status": "parsed"
      })

    except Exception as e:
      state["audit_log"].append({
        "agent": "document_parsing",
        "document_id": document_id,
        "status": "error",
        "error": str(e)
      })

  state["extracted_data"] = {"documents": extracted_documents}
  return state

def extract_fields_with_gpt(ocr_text: str) -> dict:
  system_prompt = (
    "You are a KYC document extraction system.\n"
    "Extract fields ONLY if explicitly present in the text.\n"
    "Do NOT guess or infer missing values.\n"
    "If a field is not clearly present, return null.\n"
    "Dates must be in YYYY-MM-DD format.\n"
  )

  user_prompt = f"""
  OCR TEXT:
  {ocr_text}

  Extract the following fields:
  - document_type
  - full_name
  - date_of_birth
  - address
  - expiry_date
  - confidence (0 to 1 based on clarity)
  """

  response = llm.invoke(
    [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ],
    response_format={
      "type": "json_schema",
      "json_schema": DOCUMENT_SCHEMA
    }
  )

  return response.content