from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.graph.kyc_graph import run_kyc_graph
from app.db.crud import create_kyc_case, update_kyc_result
from app.db.session import get_db
from app.db.crud import get_kyc_case
from app.db.crud import get_audit_logs

router = APIRouter()


@router.post("/submit")
def submit_kyc(payload: dict, db: Session = Depends(get_db)):

    kyc_id = create_kyc_case(db, payload["customer_id"])

    result = run_kyc_graph(
        kyc_id=kyc_id,
        documents=payload["documents"]
    )

    update_kyc_result(db, kyc_id, result)

    return {
        "kyc_id": kyc_id,
        "status": result["decision"]
    }

@router.get("/status/{kyc_id}")
def get_status(kyc_id: str, db: Session = Depends(get_db)):

    case = get_kyc_case(db, kyc_id)

    if not case:
        return {"error": "KYC case not found"}

    return {
        "kyc_id": case.kyc_id,
        "status": case.status
    }

@router.get("/result/{kyc_id}")
def get_result(kyc_id: str, db: Session = Depends(get_db)):

    case = get_kyc_case(db, kyc_id)

    if not case:
        return {"error": "KYC case not found"}

    return {
        "kyc_id": case.kyc_id,
        "decision": case.final_decision
    }

@router.get("/audit/{kyc_id}")
def get_audit(kyc_id: str, db: Session = Depends(get_db)):

    logs = get_audit_logs(db, kyc_id)

    return {
        "kyc_id": kyc_id,
        "logs": logs
    }