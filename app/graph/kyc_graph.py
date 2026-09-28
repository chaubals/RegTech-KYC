from langgraph.graph import StateGraph, START, END
from app.graph.state import KYCState

from app.agents.cross_document_consistency_agent import cross_document_consistency_agent
from app.agents.decision_agent import decision_agent
from app.agents.document_parsing_agent import document_parsing_agent
from app.agents.intake_agent import intake_agent
from app.agents.regulatory_rules_agent import regulatory_rules_agent
from app.agents.sanctions_pep_agent import sanctions_pep_screening_agent
from app.agents.human_review_agent import human_review_agent

def route_after_decision(state: KYCState) -> str:
  if state.get("decision") == "ESCALATE":
    return "human_review"
  return END

def build_kyc_graph():
  graph = StateGraph(KYCState)

  # Register nodes
  graph.add_node("intake", intake_agent)
  graph.add_node("document_parsing", document_parsing_agent)
  graph.add_node("consistency_check", cross_document_consistency_agent)
  graph.add_node("regulatory_rules", regulatory_rules_agent)
  graph.add_node("sanctions_pep", sanctions_pep_screening_agent)
  graph.add_node("decision", decision_agent)

  # Human-in-loop placeholder
  graph.add_node("human_review", human_review_agent)

  # Edges (linear flow)
  graph.add_edge(START, "intake")
  graph.add_edge("intake", "document_parsing")
  graph.add_edge("document_parsing", "consistency_check")
  graph.add_edge("consistency_check", "regulatory_rules")
  graph.add_edge("regulatory_rules", "sanctions_pep")
  graph.add_edge("sanctions_pep", "decision")

  # Conditional Edge (Human)
  graph.add_conditional_edges(
    "decision", 
    route_after_decision,
    {
      "human_review": "human_review",
      END: END,
    }
  )

  graph.add_edge("human_review", END)

  return graph.compile()

def run_kyc_graph(kyc_id, documents):
  graph = build_kyc_graph()

  initial_state = {
    "kyc_id": kyc_id,
    "documents": documents,
    "audit_log": []
  }

  final_state = graph.invoke(initial_state)

  return final_state