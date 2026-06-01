"""
Model Training - Heart Disease Classification (Basic)
======================================================
Script untuk melatih model Heart Disease Classification
menggunakan MLflow Tracking UI dengan autolog.

Author: I Kadek Rai Pramana
"""

import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
import warnings

warnings.filterwarnings('ignore')


def load_preprocessed_data(data_dir: str = 'heart_disease_preprocessing'):
    """Load data hasil preprocessing."""
    train_df = pd.read_csv(os.path.join(data_dir, 'train.csv'))
    test_df = pd.read_csv(os.path.join(data_dir, 'test.csv'))

    X_train = train_df.drop('heart_disease', axis=1)
    y_train = train_df['heart_disease']
    X_test = test_df.drop('heart_disease', axis=1)
    y_test = test_df['heart_disease']

    return X_train, X_test, y_train, y_test


def train_basic():
    """Train model dengan MLflow autolog (Basic)."""

    # Set MLflow tracking URI ke lokal
    mlflow.set_tracking_uri("http://127.0.0.1:5000")

    # Set experiment
    mlflow.set_experiment("heart-disease-basic")

    # Enable autolog
    mlflow.sklearn.autolog()

    # Load data
    X_train, X_test, y_train, y_test = load_preprocessed_data()

    with mlflow.start_run(run_name="rf_autolog"):
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Predict & evaluate
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        print(f"\nBasic Model (Autolog):")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"\n[INFO] Model logged to MLflow with autolog.")

    return model


if __name__ == '__main__':
    train_basic()
