from app.graph.state import KYCState

def human_review_agent(state: KYCState) -> KYCState:
  state["audit_log"].append({
    "agent": "human_review",
    "status": "pending_manual_revview"
  })

  return state