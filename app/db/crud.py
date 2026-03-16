import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import KYCCase, AuditLog


def create_kyc_case(db: Session, customer_id: str):

    kyc_id = str(uuid.uuid4())

    case = KYCCase(
        kyc_id=kyc_id,
        customer_id=customer_id,
        status="PROCESSING"
    )

    db.add(case)
    db.commit()

    return kyc_id


def update_kyc_result(db: Session, kyc_id: str, result: dict):

    case = db.query(KYCCase).filter(KYCCase.kyc_id == kyc_id).first()

    case.status = "COMPLETED"
    case.final_decision = result.get("decision")
    case.last_updated_at = datetime.utcnow()

    db.commit()


def get_kyc_case(db: Session, kyc_id: str):
    return db.query(KYCCase).filter(KYCCase.kyc_id == kyc_id).first()


def get_audit_logs(db: Session, kyc_id: str):

    return db.query(AuditLog).filter(
        AuditLog.kyc_id == kyc_id
    ).all()