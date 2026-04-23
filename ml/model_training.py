import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import warnings

warnings.filterwarnings('ignore')

def train_and_evaluate_models(X, y):
    """
    Trains multiple models, compares them, and returns the best one.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=20, max_depth=8, random_state=42, n_jobs=-1),
        'Logistic Regression': LogisticRegression(max_iter=500, random_state=42),
    }
    
    results = []
    best_model = None
    best_f1 = 0
    best_model_name = ""

    for name, model in models.items():
        logging.info(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Evaluate
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc = roc_auc_score(y_test, y_prob)
        
        logging.info(f"--- {name} Results ---")
        logging.info(f"Accuracy : {acc:.4f}")
        logging.info(f"Precision: {prec:.4f}")
        logging.info(f"Recall   : {rec:.4f}")
        logging.info(f"F1 Score : {f1:.4f}")
        logging.info(f"ROC AUC  : {roc:.4f}")
        
        # We select best model primarily on F1 score to balance precision/recall
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_model_name = name
            
        results.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1': f1,
            'ROC_AUC': roc
        })
        
    logging.info(f"Automatically selected best model: {best_model_name} with F1: {best_f1:.4f}")
    
    return best_model, best_model_name, results

def save_model(model, filepath='fraud_model.pkl'):
    logging.info(f"Saving model to {filepath}")
    joblib.dump(model, filepath)
    logging.info("Model saved successfully.")
