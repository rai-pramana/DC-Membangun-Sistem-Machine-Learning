"""
Model Training with Hyperparameter Tuning & Manual Logging (Skilled)
=====================================================================
Script untuk melatih model Heart Disease Classification menggunakan
MLflow Tracking UI dengan hyperparameter tuning (GridSearchCV)
dan manual logging.

Author: I Kadek Rai Pramana
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report, log_loss
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import json
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


def create_confusion_matrix_plot(y_test, predictions, save_path='confusion_matrix.png'):
    """Buat dan simpan plot confusion matrix."""
    cm = confusion_matrix(y_test, predictions)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['No Disease', 'Has Disease'],
                yticklabels=['No Disease', 'Has Disease'])
    plt.title('Confusion Matrix - Heart Disease Classification', fontsize=14)
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    return save_path


def create_feature_importance_plot(model, feature_names, save_path='feature_importance.png'):
    """Buat dan simpan plot feature importance."""
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=True)

    plt.figure(figsize=(10, 7))
    plt.barh(importance_df['feature'], importance_df['importance'], color='steelblue')
    plt.title('Feature Importance - Random Forest', fontsize=14)
    plt.xlabel('Importance', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    return save_path


def create_roc_curve_plot(y_test, pred_proba, save_path='roc_curve.png'):
    """Buat dan simpan plot ROC curve."""
    from sklearn.metrics import roc_curve, auc

    fpr, tpr, _ = roc_curve(y_test, pred_proba)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2,
             label=f'ROC Curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve - Heart Disease Classification', fontsize=14)
    plt.legend(loc='lower right', fontsize=11)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    return save_path


def train_with_tuning():
    """Train model dengan hyperparameter tuning dan manual MLflow logging."""

    # Set MLflow tracking URI ke lokal
    mlflow.set_tracking_uri("http://127.0.0.1:5000")

    # Set experiment
    mlflow.set_experiment("heart-disease-tuning")

    # Load data
    X_train, X_test, y_train, y_test = load_preprocessed_data()

    # ===========================
    # Hyperparameter Grid
    # ===========================
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    print("Starting Hyperparameter Tuning with GridSearchCV...")
    print(f"Parameter grid: {param_grid}")

    with mlflow.start_run(run_name="rf_hyperparameter_tuning"):

        # ===========================
        # GridSearchCV
        # ===========================
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(
            rf, param_grid,
            cv=5,
            scoring='f1',
            n_jobs=-1,
            verbose=1,
            return_train_score=True
        )
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_
        predictions = best_model.predict(X_test)
        pred_proba = best_model.predict_proba(X_test)[:, 1]

        # ===========================
        # Manual Logging - Parameters
        # ===========================
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_param("cv_folds", 5)
        mlflow.log_param("scoring", "f1")
        mlflow.log_param("total_combinations", len(grid_search.cv_results_['params']))

        # ===========================
        # Manual Logging - Metrics
        # ===========================
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, zero_division=0)
        recall = recall_score(y_test, predictions, zero_division=0)
        f1 = f1_score(y_test, predictions, zero_division=0)
        roc_auc = roc_auc_score(y_test, pred_proba)
        logloss = log_loss(y_test, pred_proba)

        # Training metrics
        train_predictions = best_model.predict(X_train)
        train_accuracy = accuracy_score(y_train, train_predictions)
        train_f1 = f1_score(y_train, train_predictions, zero_division=0)

        mlflow.log_metric("test_accuracy", accuracy)
        mlflow.log_metric("test_precision", precision)
        mlflow.log_metric("test_recall", recall)
        mlflow.log_metric("test_f1_score", f1)
        mlflow.log_metric("test_roc_auc", roc_auc)
        mlflow.log_metric("test_log_loss", logloss)
        mlflow.log_metric("train_accuracy", train_accuracy)
        mlflow.log_metric("train_f1_score", train_f1)
        mlflow.log_metric("best_cv_score", grid_search.best_score_)
        mlflow.log_metric("n_features", X_train.shape[1])

        # ===========================
        # Manual Logging - Artifacts
        # ===========================

        # Artifact 1: Confusion Matrix Plot
        cm_path = create_confusion_matrix_plot(y_test, predictions)
        mlflow.log_artifact(cm_path)

        # Artifact 2: Feature Importance Plot
        fi_path = create_feature_importance_plot(best_model, X_train.columns.tolist())
        mlflow.log_artifact(fi_path)

        # Artifact 3: ROC Curve Plot
        roc_path = create_roc_curve_plot(y_test, pred_proba)
        mlflow.log_artifact(roc_path)

        # Artifact 4: Classification Report (JSON)
        report = classification_report(y_test, predictions, output_dict=True)
        report_path = 'classification_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        mlflow.log_artifact(report_path)

        # Artifact 5: Feature Importance Data (CSV)
        importance_df = pd.DataFrame({
            'feature': X_train.columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        fi_csv_path = 'feature_importance.csv'
        importance_df.to_csv(fi_csv_path, index=False)
        mlflow.log_artifact(fi_csv_path)

        # ===========================
        # Log Model
        # ===========================
        mlflow.sklearn.log_model(best_model, "model")

        # ===========================
        # Print Results
        # ===========================
        print(f"\n{'='*60}")
        print("HYPERPARAMETER TUNING RESULTS")
        print(f"{'='*60}")
        print(f"Best Parameters: {grid_search.best_params_}")
        print(f"Best CV F1 Score: {grid_search.best_score_:.4f}")
        print(f"\nTest Metrics:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        print(f"  ROC AUC:   {roc_auc:.4f}")
        print(f"  Log Loss:  {logloss:.4f}")
        print(f"\nTrain Metrics:")
        print(f"  Accuracy:  {train_accuracy:.4f}")
        print(f"  F1 Score:  {train_f1:.4f}")
        print(f"{'='*60}")
        print("\n[INFO] Semua metrics dan artifacts berhasil di-log ke MLflow.")
        print("[INFO] Jalankan 'mlflow ui' untuk melihat dashboard.")

        # Cleanup temp files
        for f in [cm_path, fi_path, roc_path, report_path, fi_csv_path]:
            if os.path.exists(f):
                os.remove(f)


if __name__ == '__main__':
    train_with_tuning()
