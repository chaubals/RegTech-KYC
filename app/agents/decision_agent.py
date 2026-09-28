from app.graph.state import KYCState
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
  model="gpt-4o",
  temperature=0,
)

def decision_agent(state: KYCState) -> KYCState:
  regulatory_flags = state.get("regulatory_flags", [])
  sanctions = state.get("sanctions_report", {})
  consistency = state.get("consistency_report", {})

  decision = "APPROVE"
  decision_factors = []

  # Rule 1: Sanctions match => DECLINE
  if sanctions.get("sanctions_match"):
    decision = "DECLINE"
    decision_factors.append("Customer matched sanctions list")

  # Rule 2: PEP => ESCALATE
  elif sanctions.get("pep_match"):
    decision = "ESCALATE"
    decision_factors.append("Customer identified as Politically Exposed Person. Needs human intervention.")

  # Rule 3: EDD required => ESCALATE
  elif "EDD_REQUIRED" in regulatory_flags:
    decision = "ESCALATE"
    decision_factors.append("Enhanced Due Diligence required")

  # Rule 4: Expired documents => ESCALATE
  elif consistency.get("expired_documents"):
    decision = "ESCALATE"
    decision_factors.append("Expired identity document detected")

  # Rule 5: Clean => APPROVE
  else:
    decision_factors.append("No regulatory or sanctions risks detected")

  reasoning = generate_reasoning_with_gpt(
    decision,
    decision_factors,
    regulatory_flags,
    sanctions,
    consistency
  )

  state["decision"] = decision
  state["decision_reasoning"] = reasoning

  state["audit_log"].append({
    "agent": "decision",
    "decision": decision,
    "factors": decision_factors
  })

  return state


def generate_reasoning_with_gpt(
  decision: str,
  factors: list,
  regulatory_flags: list,
  sanctions: dict,
  consistency: dict
) -> dict:
  system_prompt = (
    "You are a financial compliance analyst. \n"
    "Explain a KYC decision clearly and conservatively. \n"
    "Do not introduce new facts. \n"
    "Base reasoning only upon the given inputs."
  )

  user_prompt = f"""
  Decision: {decision}

  Decision factors:
  {factors}

  Regulatory flags:
  {regulatory_flags}

  Sanctions report:
  {sanctions}

  Consistency report:
  {consistency}

  Generate:
  - summary (plain English)
  - factors (bullet points)
  - confidence (0 to 1)
  """

  response = llm.invoke(
    [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ],

    response_format={
      "type": "json_schema",
      "json_schema": {
        "type": "object",
        "properties": {
          "summary": {"type": "string"},
          "factors": {
            "type": "array",
            "items": {"type": "string"}
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        },
        "required": ["summary", "factors", "confidence"]
      }
    }
  )

  return response.content