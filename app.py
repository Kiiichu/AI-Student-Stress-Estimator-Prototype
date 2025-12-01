# app.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os
import signal

app = FastAPI(title="Student Stress Estimator API")

# Load model
model_bundle = joblib.load("stress_model.joblib")
model = model_bundle["model"]
FEATURE_COLUMNS = model_bundle["feature_columns"]

class PredictRequest(BaseModel):
    # UPDATED: Assignments (0 - 9)
    assignments: int = Field(..., ge=0, le=9)
    
    # UPDATED: Class Hours (10 - 40)
    class_hours: float = Field(..., ge=10, le=40)
    
    # UPDATED: Days to Exam (0 - 180)
    days_to_exam: int = Field(..., ge=0, le=180)
    
    # UPDATED: Sleep Hours (0 - 12)
    sleep_hours: float = Field(..., ge=0, le=12)

class PredictResponse(BaseModel):
    stress_score: float
    category: str
    top_factor: str
    advice: list[str]

def compute_category(score: float) -> str:
    if score < 55:
        return "Low"
    elif score < 80:
        return "Medium"
    else:
        return "High"

def generate_advice(req, score):
    # NEW LOGIC: Positive reinforcement for very low stress
    if score < 30:
        return ["🌟 Great job! You are managing your workload perfectly. Keep it up!"]

    # Standard advice logic for everyone else
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
    # Calculate impact using the NEW rules from train_model.py
    
    # 1. Assignments: 5 points per assignment
    f_assignments = req.assignments * 5.0
    
    # 2. Sleep: 5 points for every hour below 9
    f_sleep = max(0, (9 - req.sleep_hours)) * 5.0
    
    # 3. Class Hours: 0.8 points per hour (NOW ADDS STRESS)
    f_class = req.class_hours * 0.8
    
    # 4. Exam: 1 point per day closer (starting from 60 days out)
    #    If days_to_exam is 999 (no exam), min caps it at 60, resulting in 0 stress.
    days_capped = min(req.days_to_exam, 60)
    f_exam = max(0, (60 - days_capped)) * 1.0

    factors = {
        "assignments": f_assignments,
        "sleep": f_sleep,
        "class_hours": f_class,
        "exam_proximity": f_exam
    }
    
    # Identify the factor with the highest calculated stress contribution
    top = max(factors.items(), key=lambda kv: kv[1])[0]
    
    mapping = {
        "assignments": "Assignment load",
        "sleep": "Lack of sleep",
        "class_hours": "Heavy class schedule",
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
    advice = generate_advice(req, score)
    tf = top_factor(req)
    return PredictResponse(stress_score=round(score,1), category=category, top_factor=tf, advice=advice)

@app.get("/shutdown")
def shutdown_event():
    print("Shutting down backend...")
    # This kills the current process (FastAPI server)
    os.kill(os.getpid(), signal.SIGTERM)
    return {"message": "Backend shutting down..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
