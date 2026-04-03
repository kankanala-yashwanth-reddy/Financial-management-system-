"""Load risk_model.pkl and run one dummy prediction."""

import joblib
import pandas as pd

MODEL_PATH = "risk_model.pkl"
FEATURE_COLUMNS = ["age", "investment_horizon_years", "risk_tolerance_score"]


def main() -> None:
    model = joblib.load(MODEL_PATH)
    # Example: mid-career investor, moderate horizon, medium tolerance
    dummy = pd.DataFrame([[35, 12, 6]], columns=FEATURE_COLUMNS)
    pred = model.predict(dummy)[0]
    proba = model.predict_proba(dummy)
    print("Features (age, investment_horizon_years, risk_tolerance_score):", dummy.iloc[0].tolist())
    print("Predicted risk_level:", pred)
    names = list(model.classes_)
    probs = {n: float(p) for n, p in zip(names, proba[0])}
    print("Class probabilities:", probs)


if __name__ == "__main__":
    main()
