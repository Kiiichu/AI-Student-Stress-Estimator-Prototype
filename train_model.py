import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

def train_with_rules():
    print("Loading dataset...")
    df = pd.read_csv("stress_dataset_v2.csv")

    # --- 1. ENFORCE YOUR LOGIC RULES ---
    # We recalculate the target 'stress_score' to strictly follow your 4 rules.
    
    def apply_rules(row):
        score = 0
        
        # Rule 1: More Assignments = More Stress (+5 pts each)
        score += row['assignments'] * 5.0
        
        # Rule 2: More Class Time = More Stress (+0.8 pts per hour)
        # (This fixes the conflict in the original CSV)
        score += row['class_hours'] * 0.8
        
        # Rule 3: More Sleep = Low Stress
        # We add stress only if sleep is low (below 9 hours). 
        # e.g., 5 hours sleep -> (9-5)*5 = 20 stress. 
        score += max(0, (9 - row['sleep_hours'])) * 5.0
        
        # Rule 4: Small Day Remaining = More Stress
        # We add stress as the exam gets closer (starting from 60 days out).
        # e.g., 1 day away -> (60-1) = 59 stress.
        score += max(0, (60 - row['days_to_exam'])) * 1.0

        # Add small random noise to make it realistic (not just a calculator)
        score += np.random.normal(0, 3)
        
        return np.clip(score, 0, 100)

    # Overwrite the stress column with our new rule-based values
    df['stress_level'] = df.apply(apply_rules, axis=1)
    print("Stress scores recalculated to match your logic.")

    # --- 2. PREPARE DATA ---
    X = df[["assignments", "class_hours", "days_to_exam", "sleep_hours"]].copy()
    y = df["stress_level"]

    # Feature Engineering (Must match app.py)
    X["exam_soon"] = (X["days_to_exam"] < 21).astype(int)
    X["days_to_exam"] = X["days_to_exam"].apply(lambda x: min(x, 60))

    # --- 3. TRAIN MODEL ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    model = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    mse = mean_squared_error(y_test, model.predict(X_test))
    print(f"Training Complete. Test MSE: {mse:.3f}")

    # Save
    joblib.dump({
        "model": model,
        "feature_columns": list(X.columns)
    }, "stress_model.joblib")
    print("Saved stress_model.joblib")

if __name__ == "__main__":
    train_with_rules()
