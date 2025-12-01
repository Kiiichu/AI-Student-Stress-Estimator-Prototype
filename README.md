# Student Stress Estimator
A desktop-based stress estimation system for students, combining a FastAPI backend with a Gradio frontend. The system predicts a student’s stress level based on assignment load, class hours, sleep, and proximity of upcoming exams. It provides stress scores, categories, top stress factors, and personalized advice.

# Features
- Stress Prediction: Uses a trained Random Forest Regressor to predict stress score (0-100).
- Stress Categories:
    - Low: 0–45
    - Medium: 45–75
    - High: 75–100
- Top Stress Factor Identification: Determines which factor contributes most to the predicted stress.
- Personalized Advice: Generates study, sleep, and exam tips based on user inputs.
- Interactive Frontend: Built with Gradio for easy user interaction.
- Portable Launcher: Includes a Python launcher to start the backend and frontend simultaneously.

# System Components
1) Backend (app.py)
- Built with FastAPI.
- Loads a pre-trained stress model (stress_model.joblib).
- Provides /predict API endpoint accepting:
    - assignments (int)
    - class_hours (float)
    - days_to_exam (int)
    - sleep_hours (float)
- Returns: stress_score, category, top_factor, and advice list.

# Frontend (gradio_stress_visual.py)
- Interactive UI for users to input their data.
- Displays stress score on a gauge and shows stress category, top factor, and advice.
- Can optionally include a "shutdown" button to close the backend.

# Launcher (launcher.py)
- Starts the backend in a separate console.
- Waits for backend readiness.
- Launches the frontend in the same process.
- Opens the default browser to the frontend URL.

# Training Script (train_model.py)
- Generates a synthetic dataset simulating student stress.
- Trains a Random Forest Regressor on assignment, class hours, sleep, and exam proximity.
- Saves the model and feature columns as stress_model.joblib.
- Ensures predictions fall within realistic Low/Medium/High ranges.

# Dataset Generator (generate_stress_dataset.py) (Optional)
- Generates a CSV dataset (stress_dataset.csv) with realistic student stress scenarios.
- Can be used for retraining or improving model accuracy.

# Installation
#Create virtual environment (optional but recommended)
python -m venv venv
source venv/Scripts/activate  # Windows
#Install dependencies
pip install -r requirements.txt
#Run launcher
python launcher.py

# Usage
- Input your data in the frontend fields: assignments, class hours, sleep hours, and days to exam.
- View the stress score, category, top stress factor, and personalized advice.
- Close the web tab or press the optional shutdown button to stop the server.

# Notes
- The system works in a virtual environment but can run outside as long as Python dependencies are satisfied.
- The model is synthetic but can be retrained with real data for better accuracy.
- Stress scoring can be fine-tuned via the training script to match realistic student scenarios.
