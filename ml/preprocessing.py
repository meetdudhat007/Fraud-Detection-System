import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import logging

def load_and_preprocess_data(file_path, chunksize=100000):
    """
    Loads dataset in chunks to optimize memory usage (for ~450MB file).
    Preprocesses data incrementally.
    """
    logging.info(f"Loading data from {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset {file_path} not found. Please place the dataset here.")

    processed_chunks = []
    
    # We will compute a consistent LabelEncoder for 'type'
    # The types are usually: PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN
    # We'll map them manually to be consistent with the backend heuristic.
    type_mapping = {
        'PAYMENT': 0,
        'TRANSFER': 1,
        'CASH_OUT': 2,
        'DEBIT': 3,
        'CASH_IN': 4
    }

    # Iterate through chunks
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize)):
        logging.info(f"Processing chunk {i+1}...")
        
        # Drop columns early
        columns_to_drop = ['nameOrig', 'nameDest', 'isFlaggedFraud']
        chunk = chunk.drop(columns=[c for c in columns_to_drop if c in chunk.columns], errors='ignore')

        # Encode 'type'
        chunk['type'] = chunk['type'].map(type_mapping).fillna(-1).astype(int)
        
        # In a real environment, we'd append or train incrementally using partial_fit, 
        # but since scikit-learn models like Random Forest don't easily do partial_fit,
        # we will concatenate the scaled-down/sampled data, or we just load it all if RAM permits.
        # Since 450MB easily fits into 8GB+ RAM configs today, we can concat.
        # But to be safe on memory, we can downsample the majority class here.

        # Handle class imbalance incrementally: keep all frauds, downsample non-frauds in each chunk
        frauds = chunk[chunk['isFraud'] == 1]
        normals = chunk[chunk['isFraud'] == 0]
        
        # Downsample normal to something reasonable to balance it somewhat per chunk
        # Example: Keep 10x normals for every fraud, or if no frauds, keep a small random subset
        if len(frauds) > 0:
            normals_sampled = normals.sample(n=min(len(normals), len(frauds) * 10), random_state=42)
        else:
            normals_sampled = normals.sample(frac=0.01, random_state=42) # Keep 1% of normals if no frauds
            
        balanced_chunk = pd.concat([frauds, normals_sampled])
        processed_chunks.append(balanced_chunk)

    logging.info("Concatenating processed chunks...")
    final_df = pd.concat(processed_chunks).reset_index(drop=True)
    
    X = final_df.drop(columns=['isFraud'])
    y = final_df['isFraud']
    
    logging.info(f"Final shape for training: X={X.shape}, y={y.shape}")
    logging.info(f"Class distribution: \n{y.value_counts()}")
    
    return X, y
