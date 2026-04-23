# AI/ML Money Transaction Fraud Detection System

A complete full-stack web application that detects fraudulent financial transactions using machine learning. Features a modern React/Tailwind frontend, a Flask/Socket.io backend, and an end-to-end Python ML pipeline.

## Setup Instructions

### Pre-requisites
- Python 3.9+
- Node.js 18+

### 1. Train the ML Model
```bash
cd ml
pip install pandas scikit-learn joblib numpy
python train_model.py
```
*Note: If `dataset/data.csv` is not found, the script will automatically generate a mock dataset to ensure the system is runnable locally.*

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
*Note: The backend will run on port 5000 and automatically create a `fraud_detection.db`. Demo accounts `admin/admin123` and `user/user123` are created automatically.*

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

## Features
- **Real-time Engine**: WebSockets via Socket.IO push transactions live to the Admin.
- **AI Explainability**: Returns human-readable reasons for flagged transactions.
- **Modern UI**: Full Dark/Light mode support, glassmorphism cards, and animated gradient backgrounds.
- **Visual Analytics**: Interactive Recharts-driven heatmaps and bar charts.

## Run the Project

### Run backend
```bash
cd backend
python app.py
```

### Run frontend
```bash
cd frontend
npm.cmd run dev
```

### Demo login
- admin / admin123
- user005 / user_005

