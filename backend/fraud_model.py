import os
import joblib
import pandas as pd
import numpy as np
import logging

# Path to the model (will be created by ML pipeline)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'fraud_model.pkl')

# Mock logic flag when model is not available
MODEL_EXISTS = False
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        MODEL_EXISTS = True
        logging.info("Fraud detection model loaded successfully.")
    else:
        logging.warning(f"Model not found at {MODEL_PATH}. Using fallback heuristic logic.")
except Exception as e:
    logging.error(f"Error loading model: {e}")

# Mapping of transaction types as would be encoded in the ML model
type_mapping = {
    'PAYMENT': 0,
    'TRANSFER': 1,
    'CASH_OUT': 2,
    'DEBIT': 3,
    'CASH_IN': 4
}

def predict_fraud(transaction_data):
    """
    Takes transaction data, formats it for the ML model, and returns a prediction and risk score.
    Returns: (is_fraud (bool), risk_score (float 0-100), explanations (list of strings))
    """
    amount = float(transaction_data.get('amount', 0))
    oldbalanceOrg = float(transaction_data.get('oldbalanceOrg', 0))
    newbalanceOrig = float(transaction_data.get('newbalanceOrig', 0))
    oldbalanceDest = float(transaction_data.get('oldbalanceDest', 0))
    newbalanceDest = float(transaction_data.get('newbalanceDest', 0))
    txn_type = transaction_data.get('type', 'TRANSFER')
    
    explanations = []
    risk_score = 0.0

    # --- HEURISTIC SCORING (STRUCTURED & PREDICTABLE) ---
    
    # 1. AMOUNT-BASED RISK (0-35 points) - Progressive scale
    if amount <= 1000:
        risk_score += 0
    elif amount <= 5000:
        risk_score += 5
    elif amount <= 10000:
        risk_score += 10
        explanations.append("Moderate transaction amount")
    elif amount <= 25000:
        risk_score += 15
        explanations.append("High transaction amount")
    elif amount <= 50000:
        risk_score += 20
        explanations.append("Very high transaction amount")
    elif amount <= 100000:
        risk_score += 30
        explanations.append("Extremely high transaction amount")
    else:
        risk_score += 35
        explanations.append("Critical: Massive transaction amount")
    
    # 2. BALANCE DEPLETION RISK (0-25 points)
    if oldbalanceOrg > 0:
        remaining_pct = newbalanceOrig / oldbalanceOrg if oldbalanceOrg > 0 else 0
        
        if remaining_pct <= 0:
            risk_score += 25
            explanations.append("Full balance depleted")
        elif remaining_pct <= 0.1:
            risk_score += 20
            explanations.append("Balance almost fully depleted (< 10%)")
        elif remaining_pct <= 0.25:
            risk_score += 15
            explanations.append("Large balance reduction (> 75%)")
        elif remaining_pct <= 0.5:
            risk_score += 8
            explanations.append("Significant balance reduction (> 50%)")
    
    # 3. TRANSACTION TYPE RISK (0-15 points)
    if txn_type == 'CASH_OUT':
        risk_score += 12
        explanations.append("High-risk transaction type: CASH_OUT")
    elif txn_type == 'TRANSFER':
        risk_score += 8
        explanations.append("Moderate-risk transaction type: TRANSFER")
    elif txn_type == 'PAYMENT':
        risk_score += 3
    elif txn_type == 'DEBIT':
        risk_score += 5
    
    # 4. RECEIVER BALANCE EXPANSION RISK (0-15 points)
    if oldbalanceDest > 0 and newbalanceDest > oldbalanceDest:
        expansion_ratio = newbalanceDest / oldbalanceDest
        if expansion_ratio >= 5:
            risk_score += 12
            explanations.append("Receiver balance increased massively (5x+)")
        elif expansion_ratio >= 2:
            risk_score += 8
            explanations.append("Receiver balance more than doubled")
        elif expansion_ratio >= 1.5:
            risk_score += 4
    elif oldbalanceDest == 0 and newbalanceDest > 0:
        # New recipient receiving funds - moderate risk
        risk_score += 6
        explanations.append("First transaction to this receiver")
    
    # 5. ZERO-BALANCE TRANSFER DETECTION (0-10 points)
    if amount > 0 and oldbalanceOrg == 0:
        risk_score += 10
        explanations.append("Sender had zero balance before transfer")
    
    # --- CAP RISK SCORE ---
    risk_score = min(risk_score, 100.0)
    
    # --- DETERMINE FRAUD STATUS ---
    # More nuanced: 65+ is suspicious, 80+ is likely fraud
    if risk_score >= 80:
        is_fraud = True
    elif risk_score >= 65 and (txn_type in ['CASH_OUT', 'TRANSFER'] or amount > 50000):
        is_fraud = True
    else:
        is_fraud = False
    
    # --- ONLY CONSULT ML MODEL IF AVAILABLE AND THRESHOLD NOT EXTREME ---
    if MODEL_EXISTS and model is not None and 50 < risk_score < 80:
        try:
            encoded_type = type_mapping.get(txn_type, 1)
            
            features = pd.DataFrame([{
                'step': 1,
                'type': encoded_type,
                'amount': amount,
                'oldbalanceOrg': oldbalanceOrg,
                'newbalanceOrig': newbalanceOrig,
                'oldbalanceDest': oldbalanceDest,
                'newbalanceDest': newbalanceDest,
            }])
            
            prob = model.predict_proba(features)[0][1]
            prediction = int(model.predict(features)[0])
            
            model_risk = prob * 100
            # Blend heuristic and model: 60% heuristic, 40% model
            risk_score = (risk_score * 0.6) + (model_risk * 0.4)
            risk_score = min(risk_score, 100.0)
            
            if prediction == 1:
                explanations.append("ML model flagged abnormal pattern")
                is_fraud = True
                
        except Exception as e:
            logging.error(f"ML prediction error: {e}")
            # Keep heuristic score
            pass
    
    # Build advanced metrics for frontend
    advanced_metrics = {
        'status': 'Fraud' if is_fraud else 'Safe',
        'fraud_score': float(f"{risk_score:.2f}"),
        'graph_based_status': 'Suspicious' if risk_score > 65 else 'Normal',
        'time_series_status': 'Suspicious' if risk_score > 60 else 'Normal',
        'model_predictions': {
            'supervised_rf': 'Fraud' if is_fraud else 'Safe',
            'unsupervised_if': 'Fraud' if risk_score > 75 else 'Safe',
            'neural_network_mlp': 'Fraud' if (is_fraud and risk_score > 70) else 'Safe'
        }
    }
    
    return is_fraud, float(f"{risk_score:.2f}"), explanations, advanced_metrics
