from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from app.db.session import Base


class KYCCase(Base):
    __tablename__ = "kyc_cases"

    kyc_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String)
    status = Column(String)
    final_decision = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    kyc_id = Column(String, index=True)
    event = Column(String)
    log_details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow)