from app.graph.kyc_graph import build_kyc_graph

if __name__ == "__main__":
  graph = build_kyc_graph()

  initial_state = {
    "documents": [
      {
        "path": "sample_docs/passport.pdf"
      },
      {
        "path": "sample_docs/drivers_license.pdf"
      }
    ],
    "user_metadata": {
      "country": "US",
      "customer_type": "individual"
    },
    "audit_log": []
  }

  final_state = graph.invoke(initial_state)

  print("\n=== FINAL DECISION ===")
  print(final_state.get("decision"))

  print("\n=== DECISION REASONING ===")
  print(final_state.get("decision_reasoning"))

  print("\n=== AUDIT LOG ===")
  for entry in final_state.get("audit_log", []):
    print(entry)