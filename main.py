"""FastAPI backend: auth, risk quiz (ML), and dashboard portfolio breakdown."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

import database as db

FEATURE_COLUMNS = ["age", "investment_horizon_years", "risk_tolerance_score"]
MODEL_PATH = Path(__file__).resolve().parent / "risk_model.pkl"
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

PORTFOLIO_WEIGHTS: dict[str, dict[str, float]] = {
    "Low": {"stocks": 0.30, "crypto": 0.05, "bonds": 0.65},
    "Medium": {"stocks": 0.50, "crypto": 0.15, "bonds": 0.35},
    "High": {"stocks": 0.70, "crypto": 0.20, "bonds": 0.10},
}

_rf_model: Any = None


def get_rf_model() -> Any:
    global _rf_model
    if _rf_model is None:
        if not MODEL_PATH.is_file():
            raise HTTPException(
                status_code=503,
                detail=f"Model file not found at {MODEL_PATH}. Run train_model.py first.",
            )
        _rf_model = joblib.load(MODEL_PATH)
    return _rf_model


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Finance Management System API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://financialmanagementsystemrtrp.netlify.app",
        "https://*.netlify.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class LoginRequest(BaseModel):
    username: str
    password: str


class QuizRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    age: int = Field(..., ge=18, le=65)
    investment_horizon_years: int = Field(..., ge=1, le=40)
    risk_tolerance_score: int = Field(..., ge=1, le=10)


class DashboardRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    savings_amount: float = Field(..., gt=0)


@app.post("/register")
def register(body: RegisterRequest) -> dict[str, Any]:
    if db.get_user_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    user_id = db.create_user(body.username, body.password)
    return {"user_id": user_id, "username": body.username.strip(), "risk_level": None}


@app.post("/login")
def login(body: LoginRequest) -> dict[str, Any]:
    uid = db.verify_login(body.username, body.password)
    if uid is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    row = db.get_user_by_id(uid)
    if row is None:
        raise HTTPException(status_code=500, detail="User record missing")
    return {
        "user_id": uid,
        "username": row["username"],
        "risk_level": row["risk_level"],
    }


@app.post("/submit_quiz")
def submit_quiz(body: QuizRequest) -> dict[str, Any]:
    row = db.get_user_by_id(body.user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    model = get_rf_model()
    features = pd.DataFrame(
        [
            [
                body.age,
                body.investment_horizon_years,
                body.risk_tolerance_score,
            ]
        ],
        columns=FEATURE_COLUMNS,
    )
    predicted = str(model.predict(features)[0])
    db.update_user_risk_level(body.user_id, predicted)
    return {"user_id": body.user_id, "risk_level": predicted}


@app.post("/dashboard_data")
def dashboard_data(body: DashboardRequest) -> dict[str, Any]:
    row = db.get_user_by_id(body.user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    risk_level: Optional[str] = row["risk_level"]
    if risk_level is None:
        raise HTTPException(
            status_code=400,
            detail="No risk profile yet. Complete the quiz first.",
        )

    weights = PORTFOLIO_WEIGHTS.get(risk_level)
    if weights is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown risk_level in database: {risk_level!r}",
        )

    total = float(body.savings_amount)
    allocation = {
        "stocks": round(total * weights["stocks"], 2),
        "crypto": round(total * weights["crypto"], 2),
        "bonds": round(total * weights["bonds"], 2),
    }
    diff = round(total - sum(allocation.values()), 2)
    allocation["bonds"] = round(allocation["bonds"] + diff, 2)

    percentages = {k: round(v * 100, 2) for k, v in weights.items()}

    return {
        "user_id": body.user_id,
        "risk_level": risk_level,
        "savings_amount": total,
        "portfolio_breakdown": allocation,
        "percentages": percentages,
    }


if FRONTEND_DIR.is_dir():
    app.mount(
        "/app",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
