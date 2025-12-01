# app.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import numpy as np

app = FastAPI(title="Student Stress Estimator API")

# Load model
model_bundle = joblib.load("stress_model.joblib")
model = model_bundle["model"]
FEATURE_COLUMNS = model_bundle["feature_columns"]

class PredictRequest(BaseModel):
    assignments: int = Field(..., ge=0, le=50)
    class_hours: float = Field(..., ge=0, le=168)
    days_to_exam: int = Field(..., ge=0, le=999)  # use 999 if no upcoming exam
    sleep_hours: float = Field(..., ge=0, le=24)

class PredictResponse(BaseModel):
    stress_score: float
    category: str
    top_factor: str
    advice: list[str]

def compute_category(score: float) -> str:
    if score < 35:
        return "Low"
    elif score < 65:
        return "Medium"
    else:
        return "High"

def generate_advice(req):
    adv = []
    if req.sleep_hours < 6:
        adv.append("Prioritise sleep — aim for 7+ hours nightly to improve focus and memory.")
    if req.assignments >= 4:
        adv.append("Break assignments into small tasks and use time-blocking.")
    if req.days_to_exam < 7:
        adv.append("Use active recall & spaced repetition for exam prep. Make a 3-day plan.")
    if req.class_hours > 25:
        adv.append("Schedule recovery breaks between heavy class days.")
    if len(adv) == 0:
        adv.append("Your stress drivers look mild — keep consistent sleep and small breaks.")
    return adv

def top_factor(req):
    # crude heuristic to identify top factor
    factors = {
        "assignments": req.assignments * 8,
        "sleep": max(0, (7 - req.sleep_hours)) * 6,
        "class_hours": max(0, req.class_hours - 20) * 0.6,
        "exam_proximity": max(0, (21 - req.days_to_exam)) * 2 if req.days_to_exam < 999 else 0
    }
    top = max(factors.items(), key=lambda kv: kv[1])[0]
    mapping = {
        "assignments": "Assignment load",
        "sleep": "Sleep hours",
        "class_hours": "Class load",
        "exam_proximity": "Upcoming exam"
    }
    return mapping.get(top, "Other")

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Prepare features like in training
    days = min(req.days_to_exam, 60)
    exam_soon = 1 if req.days_to_exam < 21 else 0
    x = np.array([[req.assignments, req.class_hours, days, req.sleep_hours, exam_soon]])
    score = float(model.predict(x)[0])
    score = max(0.0, min(100.0, score))
    category = compute_category(score)
    advice = generate_advice(req)
    tf = top_factor(req)
    return PredictResponse(stress_score=round(score,1), category=category, top_factor=tf, advice=advice)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
