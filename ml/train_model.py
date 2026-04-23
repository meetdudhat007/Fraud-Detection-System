import os
import logging
import pandas as pd
import numpy as np
from preprocessing import load_and_preprocess_data
from model_training import train_and_evaluate_models, save_model

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATASET_PATH = os.path.join('dataset', 'data.csv')
MODEL_OUTPUT_PATH = 'fraud_model.pkl'

def generate_mock_data_if_missing():
    if not os.path.exists(DATASET_PATH):
        logging.warning(f"Dataset not found at {DATASET_PATH}. Generating a realistic mock dataset.")
        os.makedirs('dataset', exist_ok=True)
        
        # Generate 10000 rows of diverse mock data
        np.random.seed(42)
        n = 10000
        
        types = np.random.choice(['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'CASH_IN'], size=n, p=[0.35, 0.35, 0.15, 0.10, 0.05])
        amounts = np.random.exponential(scale=5000, size=n)
        oldbalances = np.random.exponential(scale=20000, size=n)
        newbalances = np.maximum(0, oldbalances - amounts)
        olddestbalances = np.random.exponential(scale=10000, size=n)
        newdestbalances = olddestbalances + amounts
        
        df = pd.DataFrame({
            'step': np.random.randint(1, 744, size=n),  # Up to 31 days
            'type': types,
            'amount': amounts,
            'nameOrig': ['C' + str(i % 1000) for i in range(n)],
            'oldbalanceOrg': oldbalances,
            'newbalanceOrig': newbalances,
            'nameDest': ['M' + str(i % 5000) for i in range(n)],
            'oldbalanceDest': olddestbalances,
            'newbalanceDest': newdestbalances,
            'isFraud': 0,
            'isFlaggedFraud': 0
        })
        
        # Inject realistic fraud patterns (~8% fraud rate)
        fraud_count = int(n * 0.08)
        fraud_idx = np.random.choice(n, size=fraud_count, replace=False)
        
        for idx in fraud_idx:
            fraud_type = np.random.choice(['TRANSFER', 'CASH_OUT'])
            df.at[idx, 'type'] = fraud_type
            
            # Pattern 1: Unusual large amount (40% of frauds)
            if np.random.random() < 0.40:
                df.at[idx, 'amount'] = np.random.uniform(50000, 500000)
                df.at[idx, 'newbalanceOrig'] = max(0, df.at[idx, 'oldbalanceOrg'] - df.at[idx, 'amount'])
            
            # Pattern 2: Account emptying (30% of frauds)
            elif np.random.random() < 0.75:
                df.at[idx, 'amount'] = df.at[idx, 'oldbalanceOrg'] * 0.95
                df.at[idx, 'newbalanceOrig'] = df.at[idx, 'oldbalanceOrg'] * 0.05
            
            # Pattern 3: Suspicious rapid sequence (20% of frauds)
            elif np.random.random() < 0.80:
                df.at[idx, 'step'] = np.random.randint(1, 10)
                df.at[idx, 'amount'] = np.random.uniform(10000, 100000)
                df.at[idx, 'newbalanceOrig'] = df.at[idx, 'oldbalanceOrg'] - df.at[idx, 'amount']
            
            # Pattern 4: New recipient + large transfer (10% of frauds)
            else:
                df.at[idx, 'oldbalanceDest'] = 0  # First transaction to this recipient
                df.at[idx, 'amount'] = np.random.uniform(20000, 150000)
                df.at[idx, 'newbalanceDest'] = df.at[idx, 'amount']
            
            df.at[idx, 'isFraud'] = 1
        
        df.to_csv(DATASET_PATH, index=False)
        logging.info(f"Saved realistic mock dataset ({fraud_count} frauds) to {DATASET_PATH}")

def main():
    logging.info("Starting ML Training Pipeline")
    
    generate_mock_data_if_missing()
    
    try:
        # Step 1-4: Load, Clean, Feature Engineering, Encoding
        X, y = load_and_preprocess_data(DATASET_PATH)
        
        # Step 5-6: Train and Evaluate Models
        best_model, best_name, results = train_and_evaluate_models(X, y)
        
        # Step 7: Save best model
        save_model(best_model, MODEL_OUTPUT_PATH)
        
        logging.info("Pipeline completed successfully.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
