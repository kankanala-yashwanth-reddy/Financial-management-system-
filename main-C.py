"""FastAPI backend: auth, risk quiz (ML), and dashboard portfolio breakdown."""

from __future__ import annotations

from contextlib import asynccontextmanager
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

FEATURE_COLUMNS = ["age", "investment_horizon_years", "risk_tolerance_score"]
MODEL_PATH = Path(__file__).resolve().parent / "risk_model.pkl"
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

COMPAT_PATHS: dict[str, str] = {
    "index.html": "index-B.html",
    "login.html": "login-B.html",
    "signup.html": "signup-B.html",
    "quiz.html": "quiz-B.html",
    "quiz-page1.html": "quiz-page1-B.html",
    "quiz-page2.html": "quiz-page2-B.html",
    "quiz-page3.html": "quiz-page3-B.html",
    "dashboard.html": "dashboard-B.html",
    "dashboard-modern.html": "dashboard-modern-B.html",
    "api.js": "api-B.js",
    "dashboard-app.js": "dashboard-app-B.js",
    "home.css": "home-B.css",
    "styles.css": "styles-B.css",
    "dashboard.css": "dashboard-B.css",
}

PORTFOLIO_WEIGHTS: dict[str, dict[str, float]] = {
    "Low": {"stocks": 0.30, "crypto": 0.05, "bonds": 0.65},
    "Medium": {"stocks": 0.50, "crypto": 0.15, "bonds": 0.35},
    "High": {"stocks": 0.70, "crypto": 0.20, "bonds": 0.10},
}

_rf_model: Any = None


def _load_db_module() -> Any:
    db_path = Path(__file__).resolve().parent / "database-C.py"
    spec = spec_from_file_location("database_C", db_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load database module from {db_path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


db = _load_db_module()


def get_rf_model() -> Any:
    global _rf_model
    if _rf_model is None:
        if not MODEL_PATH.is_file():
            raise HTTPException(
                status_code=503,
                detail=f"Model file not found at {MODEL_PATH}. Run train_model-A.py first.",
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


@app.get("/app", include_in_schema=False)
@app.get("/app/{requested_path:path}", include_in_schema=False)
def frontend_file(requested_path: str = "") -> FileResponse:
    if not requested_path:
        target = FRONTEND_DIR / "index-B.html"
    else:
        requested_path = COMPAT_PATHS.get(requested_path, requested_path)
        target = (FRONTEND_DIR / requested_path).resolve()
        frontend_root = FRONTEND_DIR.resolve()
        if frontend_root not in target.parents and target != frontend_root:
            raise HTTPException(status_code=404, detail="File not found")

    if target.is_dir():
        target = target / "index-B.html"
    if not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
