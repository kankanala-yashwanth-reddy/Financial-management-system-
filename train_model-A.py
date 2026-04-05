
"""
Generate mock finance survey data, label risk_level from features, train Random Forest, export model.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

RANDOM_STATE = 42
N_ROWS = 200
FEATURE_COLUMNS = ["age", "investment_horizon_years", "risk_tolerance_score"]
MODEL_PATH = "risk_model.pkl"


def label_risk_level(df: pd.DataFrame) -> pd.Series:
    """
    Derive risk_level from features (higher score → higher risk appetite).
    Combines risk tolerance, horizon length, and youth as a weighted index.
    """
    tol = (df["risk_tolerance_score"] - 1) / 9.0
    horizon = (df["investment_horizon_years"] - 1) / 39.0
    youth = (65 - df["age"]) / (65 - 18.0)
    index_score = 0.45 * tol + 0.35 * horizon + 0.20 * youth

    risk = pd.Series("Medium", index=df.index, dtype="object")
    risk[index_score < 0.36] = "Low"
    risk[index_score > 0.64] = "High"
    return risk


def build_dataset(n_rows: int, rng: np.random.Generator) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "age": rng.integers(18, 66, size=n_rows),
            "investment_horizon_years": rng.integers(1, 41, size=n_rows),
            "risk_tolerance_score": rng.integers(1, 11, size=n_rows),
        }
    )
    df["risk_level"] = label_risk_level(df)
    return df


def main() -> None:
    rng = np.random.default_rng(RANDOM_STATE)
    data = build_dataset(N_ROWS, rng)

    X = data[FEATURE_COLUMNS]
    y = data["risk_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    train_acc = clf.score(X_train, y_train)
    test_acc = clf.score(X_test, y_test)
    print(f"Train accuracy: {train_acc:.3f}")
    print(f"Test accuracy:  {test_acc:.3f}")
    print(f"Label counts:\n{data['risk_level'].value_counts()}")

    joblib.dump(clf, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
