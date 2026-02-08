from app.graph.state import KYCState

#No logic here. We're just intaking the document and initializing the audit log

#OCR will be done in document parsing agent

def intake_agent(state: KYCState) -> KYCState:
  state["audit_log"].append({
    "agent": "intake",
    "status": "document_received",
  })
  return state

