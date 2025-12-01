import gradio as gr
import requests
import os
import sys

# ----------- Configuration -----------
API_URL = "http://127.0.0.1:8000/predict"

# ----------- Custom CSS (Dark Blue Theme + Horizontal Fix) -----------
CUSTOM_CSS = """
/* 1. The Main Page Background (Blue Gradient) */
.gradio-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* 2. The Central Card (Dark Glass Effect) */
#main-card {
    background: rgba(17, 24, 39, 0.95); /* Very dark blue/grey */
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    
    /* --- THE FIX IS HERE --- */
    max-width: 1000px;
    min-width: 850px; /* <--- This forces it to stay wide (horizontal) */
    width: 100%;
}

/* 3. Text Colors - Force White for Visibility */
#main-card h1, #main-card h2, #main-card h3, #main-card p, #main-card span, #main-card label {
    color: #ffffff !important;
}

/* 4. Input Sliders Styling */
input[type=range] {
    filter: hue-rotate(180deg); 
}

/* 5. The Advice Box */
.advice-box {
    background-color: #374151; 
    border-left: 5px solid #fbbf24; 
    color: #f3f4f6; 
    padding: 15px;
    border-radius: 8px;
    margin-top: 20px;
    font-size: 15px;
    line-height: 1.6;
}

/* 6. Category Header Styling */
.category-header {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 10px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
"""

# ----------- Backend Logic -----------
def predict_stress(assignments, class_hours, days_until_exam, sleep_hours):
    payload = {
        "assignments": assignments,
        "class_hours": class_hours,
        "days_to_exam": days_until_exam,
        "sleep_hours": sleep_hours
    }

    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        
        score = data.get("stress_score", 0)
        category = data.get("category", "Unknown")
        advice = data.get("advice", [])

    except:
        # Fallback for Demo
        score = 62
        category = "Medium"
        advice = ["Ensure you are running your FastAPI backend!", "Take short breaks."]

    # UPDATED: Thresholds set to 40 and 60 to match app.py logic
    if score < 40:
        emoji = "😌"
        color = "#4ade80" # Green
    elif score < 60:
        emoji = "😐"
        color = "#facc15" # Yellow
    else:
        emoji = "😫"
        color = "#f87171" # Red

    return score, category, emoji, color, advice

# ----------- System Control -----------
def shutdown_system():
    # 1. Tell backend to shut down
    try:
        requests.get(API_URL.replace("/predict", "/shutdown"))
    except:
        pass # Backend might die before replying, which is fine
    
    # 2. Kill this frontend process
    print("Shutting down frontend...")
    os._exit(0)

# ----------- HTML Generators -----------

def build_gauge_html(score, color):
    # Convert score (0-100) to degrees (0-180)
    angle = (score / 100) * 180
    
    return f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:20px;">
        
        <div style="position: relative; width: 220px; height: 110px; overflow: hidden;">
            
            <div style="
                position: absolute; top: 0; left: 0;
                width: 220px; height: 220px; 
                background: #374151; 
                border-radius: 50%;
            "></div>

            <div style="
                position: absolute; top: 0; left: 0;
                width: 220px; height: 220px;
                background: conic-gradient(from 270deg, {color} 0deg, {color} {angle}deg, transparent {angle}deg);
                border-radius: 50%;
                opacity: 0.9;
            "></div>

            <div style="
                position: absolute; top: 25px; left: 25px;
                width: 170px; height: 170px;
                background: #111827; 
                border-radius: 50%;
                display: flex; justify-content: center; align-items: flex-start;
            "></div>

        </div>

        <div style="font-size: 48px; font-weight: bold; color: {color}; margin-top: -55px; z-index:10; text-shadow: 0 0 15px {color};">
            {score:.0f}
        </div>
    </div>
    """

def format_output(assignments, class_hours, days_until_exam, sleep_hours):
    score, category, emoji, color, advice_list = predict_stress(assignments, class_hours, days_until_exam, sleep_hours)
    
    category_html = f"<div class='category-header' style='color:{color}'>{category} {emoji}</div>"
    gauge_html = build_gauge_html(score, color)
    
    advice_items = "".join([f"<li style='margin-bottom:5px;'>{item}</li>" for item in advice_list])
    advice_html = f"""
    <div class='advice-box'>
        <strong style="color: #fbbf24;">💡 Recommendations:</strong>
        <ul style='padding-left: 20px; margin-top: 8px; color: #e5e7eb;'>
            {advice_items}
        </ul>
    </div>
    """
    
    return category_html, gauge_html, advice_html

# ----------- GRADIO UI -----------
with gr.Blocks(theme=gr.themes.Soft(), css=CUSTOM_CSS) as demo:

    with gr.Column(elem_id="main-card"):
        
        gr.Markdown("# 🧬 Student Stress Estimator", elem_classes="text-center")
        
        with gr.Row():
            
            # ---------- LEFT: INPUTS ----------
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 🍃 Your Inputs")
                
                # Sliders with updated ranges
                assignments = gr.Slider(0, 9, value=4, step=1, label="Assignments Due")
                class_hours = gr.Slider(10, 40, value=20, step=1, label="Class Hours / Week")
                sleep_hours = gr.Slider(0, 12, value=6, step=0.5, label="Sleep Hours / Night")
                days_until_exam = gr.Slider(0, 180, value=30, step=1, label="Days Until Exam")

            # ---------- RIGHT: RESULTS ----------
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 📊 Analysis")
                out_category = gr.HTML(value="<div class='category-header' style='color:#6b7280'>Ready?</div>")
                out_gauge = gr.HTML(build_gauge_html(0, "#4b5563"))
                out_advice = gr.HTML("<div class='advice-box'>Adjust sliders and click Analyze.</div>")

        # Analyze Button
        predict_btn = gr.Button("Analyze Stress Level", variant="primary", size="lg")
        
        # Shutdown Button
        shutdown_btn = gr.Button("🔴 Shutdown System", variant="stop")

    # Click Events
    predict_btn.click(
        fn=format_output,
        inputs=[assignments, class_hours, days_until_exam, sleep_hours],
        outputs=[out_category, out_gauge, out_advice]
    )
    
    shutdown_btn.click(fn=shutdown_system)

demo.launch(share=False, inbrowser=True, server_name="127.0.0.1", server_port=7860)
