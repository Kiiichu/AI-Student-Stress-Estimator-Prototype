# train_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import random

# --- 1. Simulate dataset ---
def simulate_row():
    """
    Simulate one student's weekly stress scenario.
    Returns a dict with inputs and computed stress score.
    """
    # Inputs:
    # assignments: 0-8 (count due this week)
    # class_hours: 0-30 (hours per week)
    # days_to_exam: 0-60 (days until next exam) - if no exam, use 999
    # sleep_hours: 3-12 (avg hours)
    a = np.random.poisson(2)  # assignments
    a = min(a, 8)
    ch = np.random.normal(15, 6)  # class hours
    ch = max(0, min(30, ch))
    # sometimes no imminent exam
    d_exam = 999 if random.random() < 0.25 else int(max(0, np.random.exponential(10)))
    sleep = np.random.normal(7, 1.5)
    sleep = max(3, min(12, sleep))

    # --- Compute stress score ---
    stress = 0
    stress += a * 6                   # assignments weight slightly reduced
    stress += max(0, (7 - sleep)) * 5 # low sleep increases stress
    stress += max(0, (ch - 15)) * 0.5 # only above 15h/week adds mild stress
    if d_exam != 999:
        stress += max(0, (21 - d_exam)) * 1.5  # exam proximity effect
    stress += np.random.normal(0, 4)  # reduced random noise
    stress = np.clip(stress, 0, 100)

    return {
        "assignments": a,
        "class_hours": ch,
        "days_to_exam": d_exam if d_exam < 999 else 999,
        "sleep_hours": sleep,
        "stress_score": stress
    }

def generate_dataset(n=5000):
    return pd.DataFrame([simulate_row() for _ in range(n)])

# --- 2. Train model ---
def train_and_save():
    df = generate_dataset(5000)
    X = df[["assignments", "class_hours", "days_to_exam", "sleep_hours"]].copy()
    # Add boolean feature for upcoming exam
    X["exam_soon"] = (X["days_to_exam"] < 21).astype(int)
    # Cap days_to_exam for model stability
    X["days_to_exam"] = X["days_to_exam"].apply(lambda x: min(x, 60))
    y = df["stress_score"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    # Train RandomForest
    model = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    pred = model.predict(X_test)
    mse = mean_squared_error(y_test, pred)
    print(f"Test MSE: {mse:.3f}")

    # Save
    joblib.dump({
        "model": model,
        "feature_columns": list(X.columns)
    }, "stress_model.joblib")
    print("Saved stress_model.joblib")

if __name__ == "__main__":
    train_and_save()
