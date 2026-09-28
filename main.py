from fastapi import FastAPI
from app.graph.kyc_graph import build_kyc_graph
from app.db.session import engine
from app.db.models import Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Db Setup - run once on startup
  Base.metadata.create_all(bind=engine)
  yield

app = FastAPI(title="RegTech KYC Engine", lifespan=lifespan)