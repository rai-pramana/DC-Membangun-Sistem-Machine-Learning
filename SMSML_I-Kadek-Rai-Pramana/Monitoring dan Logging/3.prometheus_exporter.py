"""
Prometheus Exporter & Model Serving - Heart Disease Classification
===================================================================
Flask API server yang melakukan serving model Heart Disease Classification
dan mengekspos metrik Prometheus untuk monitoring.

Author: I Kadek Rai Pramana

Metrik yang diekspos:
1. ml_request_total (Counter) - Total request
2. ml_request_latency_seconds (Histogram) - Latency per request
3. ml_prediction_output_total (Counter) - Distribusi prediksi
4. ml_model_accuracy (Gauge) - Akurasi model
5. ml_system_cpu_percent (Gauge) - CPU usage
6. ml_system_memory_percent (Gauge) - Memory usage
7. ml_request_error_total (Counter) - Error count
8. ml_model_load_time_seconds (Gauge) - Model load time
9. ml_feature_count (Gauge) - Jumlah fitur
10. ml_active_requests (Gauge) - Active concurrent requests
"""

import time
import os
import sys
import threading
import psutil
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest,
    CollectorRegistry, CONTENT_TYPE_LATEST
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ===========================
# Configuration
# ===========================
MODEL_DIR = 'heart_disease_preprocessing'
PORT = 5001

app = Flask(__name__)

# ===========================
# Prometheus Metrics Registry
# ===========================
registry = CollectorRegistry(auto_describe=True)

# 1. Total Requests
REQUEST_TOTAL = Counter(
    'ml_request_total',
    'Total number of prediction requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

# 2. Request Latency
REQUEST_LATENCY = Histogram(
    'ml_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=registry
)

# 3. Prediction Output Distribution
PREDICTION_OUTPUT = Counter(
    'ml_prediction_output_total',
    'Distribution of prediction outputs',
    ['app', 'prediction_class'],
    registry=registry
)

# 4. Model Accuracy
MODEL_ACCURACY = Gauge(
    'ml_model_accuracy',
    'Current model accuracy on test set',
    ['app', 'model_type'],
    registry=registry
)

# 5. CPU Usage
CPU_USAGE = Gauge(
    'ml_system_cpu_percent',
    'System CPU usage percentage',
    ['app'],
    registry=registry
)

# 6. Memory Usage
MEMORY_USAGE = Gauge(
    'ml_system_memory_percent',
    'System memory usage percentage',
    ['app'],
    registry=registry
)

# 7. Error Count
ERROR_TOTAL = Counter(
    'ml_request_error_total',
    'Total number of request errors',
    ['app', 'error_type'],
    registry=registry
)

# 8. Model Load Time
MODEL_LOAD_TIME = Gauge(
    'ml_model_load_time_seconds',
    'Time taken to load the model',
    ['app'],
    registry=registry
)

# 9. Feature Count
FEATURE_COUNT = Gauge(
    'ml_feature_count',
    'Number of features used by the model',
    ['app'],
    registry=registry
)

# 10. Active Requests
ACTIVE_REQUESTS = Gauge(
    'ml_active_requests',
    'Number of currently active requests',
    ['app'],
    registry=registry
)

# ===========================
# Model & Data Loading
# ===========================
FEATURE_NAMES = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

model = None
scaler = None
test_accuracy = 0.0


def load_model_and_data():
    """Load atau train model untuk serving."""
    global model, scaler, test_accuracy

    start_time = time.time()

    # Load preprocessed data
    train_df = pd.read_csv(os.path.join(MODEL_DIR, 'train.csv'))
    test_df = pd.read_csv(os.path.join(MODEL_DIR, 'test.csv'))

    X_train = train_df.drop('heart_disease', axis=1)
    y_train = train_df['heart_disease']
    X_test = test_df.drop('heart_disease', axis=1)
    y_test = test_df['heart_disease']

    # Load scaler
    scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)

    # Train model
    model = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42
    )
    model.fit(X_train, y_train)

    # Calculate accuracy
    predictions = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, predictions)

    load_time = time.time() - start_time

    # Set static metrics
    APP = 'heart-disease-classifier'
    MODEL_ACCURACY.labels(app=APP, model_type='RandomForest').set(test_accuracy)
    MODEL_LOAD_TIME.labels(app=APP).set(load_time)
    FEATURE_COUNT.labels(app=APP).set(len(FEATURE_NAMES))

    print(f"[INFO] Model loaded in {load_time:.2f}s, accuracy: {test_accuracy:.4f}")


def update_system_metrics():
    """Background thread untuk update sistem metrik."""
    APP = 'heart-disease-classifier'
    while True:
        try:
            CPU_USAGE.labels(app=APP).set(psutil.cpu_percent(interval=1))
            MEMORY_USAGE.labels(app=APP).set(psutil.virtual_memory().percent)
        except Exception:
            pass
        time.sleep(5)


# ===========================
# Flask Routes
# ===========================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'model_accuracy': round(test_accuracy, 4)
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint."""
    APP = 'heart-disease-classifier'
    ACTIVE_REQUESTS.labels(app=APP).inc()
    start_time = time.time()

    try:
        data = request.get_json(force=True)

        # Support single and batch predictions
        if 'features' in data:
            features = data['features']
        elif 'data' in data:
            features = data['data']
        else:
            features = [data]

        if not isinstance(features[0], list):
            features = [features]

        # Create DataFrame
        df = pd.DataFrame(features, columns=FEATURE_NAMES[:len(features[0])])

        # Predict
        predictions = model.predict(df).tolist()
        probabilities = model.predict_proba(df).tolist()

        # Update metrics
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint='/predict').observe(latency)
        REQUEST_TOTAL.labels(method='POST', endpoint='/predict', status='200').inc()

        for pred in predictions:
            label = 'has_disease' if pred == 1 else 'no_disease'
            PREDICTION_OUTPUT.labels(app=APP, prediction_class=label).inc()

        result = {
            'predictions': predictions,
            'probabilities': probabilities,
            'labels': ['no_disease' if p == 0 else 'has_disease' for p in predictions],
            'latency_ms': round(latency * 1000, 2)
        }

        return jsonify(result)

    except Exception as e:
        ERROR_TOTAL.labels(app=APP, error_type=type(e).__name__).inc()
        REQUEST_TOTAL.labels(method='POST', endpoint='/predict', status='500').inc()
        return jsonify({'error': str(e)}), 500

    finally:
        ACTIVE_REQUESTS.labels(app=APP).dec()


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(registry), 200, {'Content-Type': CONTENT_TYPE_LATEST}


# ===========================
# Main
# ===========================
if __name__ == '__main__':
    print("=" * 60)
    print("HEART DISEASE ML MODEL SERVER")
    print("=" * 60)

    # Load model
    load_model_and_data()

    # Start background metrics thread
    metrics_thread = threading.Thread(target=update_system_metrics, daemon=True)
    metrics_thread.start()

    print(f"\n[INFO] Server starting on port {PORT}")
    print(f"[INFO] Endpoints:")
    print(f"  - Health: http://localhost:{PORT}/health")
    print(f"  - Predict: http://localhost:{PORT}/predict")
    print(f"  - Metrics: http://localhost:{PORT}/metrics")

    app.run(host='0.0.0.0', port=PORT, debug=False)
