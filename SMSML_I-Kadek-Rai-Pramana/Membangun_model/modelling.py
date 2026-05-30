"""
Model Training with MLflow Autolog (Basic)
============================================
Script untuk melatih model Wine Quality Classification
menggunakan MLflow Tracking UI dengan autolog.

Author: I Kadek Rai Pramana
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import os
import warnings

warnings.filterwarnings('ignore')


def load_preprocessed_data(data_dir: str = 'wine_quality_preprocessing'):
    """Load data hasil preprocessing."""
    train_df = pd.read_csv(os.path.join(data_dir, 'train.csv'))
    test_df = pd.read_csv(os.path.join(data_dir, 'test.csv'))

    X_train = train_df.drop('quality_label', axis=1)
    y_train = train_df['quality_label']
    X_test = test_df.drop('quality_label', axis=1)
    y_test = test_df['quality_label']

    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test, y_train, y_test


def train_model():
    """Train Random Forest model dengan MLflow autolog."""

    # Set MLflow tracking URI ke lokal
    mlflow.set_tracking_uri("http://127.0.0.1:5000")

    # Set experiment
    mlflow.set_experiment("wine-quality-classification")

    # Enable autolog
    mlflow.sklearn.autolog()

    # Load data
    X_train, X_test, y_train, y_test = load_preprocessed_data()

    with mlflow.start_run(run_name="random_forest_autolog"):
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Evaluate
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        print(f"\n{'='*50}")
        print(f"Model: RandomForestClassifier (Autolog)")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"{'='*50}")
        print("\nClassification Report:")
        print(classification_report(y_test, predictions,
                                    target_names=['Not Good', 'Good']))

        print("\n[INFO] Model dan artefak berhasil disimpan ke MLflow Tracking UI.")
        print("[INFO] Jalankan 'mlflow ui' untuk melihat dashboard.")


if __name__ == '__main__':
    train_model()
