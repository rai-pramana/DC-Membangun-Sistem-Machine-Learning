"""
Prometheus Metrics Exporter for Wine Quality ML Model
======================================================
Script ini menjalankan Flask server yang:
1. Melayani prediksi model (serving)
2. Mengexpose metrics untuk Prometheus scraping
3. Memonitor performa sistem dan model

Author: I Kadek Rai Pramana
Metrics yang dimonitor (10 metriks untuk level Advance):
  1. ml_request_total - Total prediction requests
  2. ml_prediction_latency_seconds - Prediction latency
  3. ml_prediction_output_total - Prediction result distribution
  4. ml_prediction_confidence - Model confidence scores
  5. ml_system_cpu_percent - CPU usage
  6. ml_system_memory_percent - Memory usage
  7. ml_active_requests - Active concurrent requests
  8. ml_errors_total - Total errors by type
  9. ml_request_size_bytes - Request payload size
  10. ml_model_info - Model metadata info
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    generate_latest, CONTENT_TYPE_LATEST
)
from flask import Flask, request, jsonify, Response
import pandas as pd
import numpy as np
import time
import psutil
import os
import pickle
import joblib
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)

# ============================================================
# PROMETHEUS METRICS DEFINITION (10 Metriks)
# ============================================================

# 1. Total request counter
REQUEST_COUNT = Counter(
    'ml_request_total',
    'Total number of prediction requests',
    ['method', 'endpoint', 'status']
)

# 2. Prediction latency
PREDICTION_LATENCY = Histogram(
    'ml_prediction_latency_seconds',
    'Time spent processing prediction requests',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# 3. Prediction output distribution
PREDICTION_OUTPUT = Counter(
    'ml_prediction_output_total',
    'Distribution of prediction outputs',
    ['prediction_class']
)

# 4. Model confidence scores
PREDICTION_CONFIDENCE = Histogram(
    'ml_prediction_confidence',
    'Confidence score distribution of predictions',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
)

# 5. CPU usage
CPU_USAGE = Gauge(
    'ml_system_cpu_percent',
    'Current system CPU usage percentage'
)

# 6. Memory usage
MEMORY_USAGE = Gauge(
    'ml_system_memory_percent',
    'Current system memory usage percentage'
)

# 7. Active concurrent requests
ACTIVE_REQUESTS = Gauge(
    'ml_active_requests',
    'Number of requests currently being processed'
)

# 8. Error counter
ERROR_COUNT = Counter(
    'ml_errors_total',
    'Total number of errors encountered',
    ['error_type']
)

# 9. Request size
REQUEST_SIZE = Histogram(
    'ml_request_size_bytes',
    'Size of incoming request payloads in bytes',
    buckets=[50, 100, 250, 500, 1000, 2500, 5000, 10000]
)

# 10. Model info
MODEL_INFO = Info(
    'ml_model',
    'Information about the currently loaded ML model'
)

# ============================================================
# MODEL LOADING
# ============================================================

model = None
FEATURE_NAMES = [
    'fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar',
    'chlorides', 'free sulfur dioxide', 'total sulfur dioxide', 'density',
    'pH', 'sulphates', 'alcohol'
]


def load_model():
    """Load model dari MLflow artifacts atau file lokal."""
    global model

    # Coba load dari MLflow
    model_uri = os.getenv("MODEL_URI", "")
    if model_uri:
        try:
            import mlflow
            model = mlflow.pyfunc.load_model(model_uri)
            MODEL_INFO.info({
                'model_type': 'mlflow_pyfunc',
                'model_uri': model_uri,
                'status': 'loaded'
            })
            print(f"[INFO] Model loaded from MLflow: {model_uri}")
            return
        except Exception as e:
            print(f"[WARN] Failed to load MLflow model: {e}")

    # Fallback: train model sederhana
    print("[INFO] Training fallback model for serving...")
    from sklearn.ensemble import RandomForestClassifier

    train_path = os.getenv("TRAIN_DATA", "wine_quality_preprocessing/train.csv")
    if os.path.exists(train_path):
        train_df = pd.read_csv(train_path)
        X_train = train_df.drop('quality_label', axis=1)
        y_train = train_df['quality_label']
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        MODEL_INFO.info({
            'model_type': 'RandomForestClassifier',
            'model_uri': 'fallback_local',
            'status': 'loaded',
            'n_features': str(X_train.shape[1])
        })
        print(f"[INFO] Fallback model trained and ready.")
    else:
        print(f"[ERROR] No model or training data found at {train_path}")
        MODEL_INFO.info({
            'model_type': 'none',
            'model_uri': 'none',
            'status': 'not_loaded'
        })


# ============================================================
# MIDDLEWARE
# ============================================================

@app.before_request
def before_request():
    """Track request start time and active requests."""
    request.start_time = time.time()
    ACTIVE_REQUESTS.inc()


@app.after_request
def after_request(response):
    """Update system metrics after each request."""
    ACTIVE_REQUESTS.dec()
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    return response


# ============================================================
# ENDPOINTS
# ============================================================

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint untuk prediksi wine quality.

    Request body (JSON):
    {
        "fixed acidity": 7.4,
        "volatile acidity": 0.7,
        "citric acid": 0.0,
        "residual sugar": 1.9,
        "chlorides": 0.076,
        "free sulfur dioxide": 11.0,
        "total sulfur dioxide": 34.0,
        "density": 0.9978,
        "pH": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4
    }
    """
    try:
        data = request.get_json()
        REQUEST_SIZE.observe(len(request.data))

        if model is None:
            ERROR_COUNT.labels(error_type='ModelNotLoaded').inc()
            REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='503').inc()
            return jsonify({'error': 'Model not loaded'}), 503

        # Buat DataFrame dari input
        df = pd.DataFrame([data])

        # Prediksi dengan timing
        start = time.time()

        # Handle MLflow pyfunc model vs sklearn model
        if hasattr(model, 'predict_proba'):
            prediction = model.predict(df)
            confidence = model.predict_proba(df).max(axis=1)[0]
        else:
            prediction = model.predict(df)
            confidence = 0.5  # pyfunc model doesn't always have predict_proba

        latency = time.time() - start

        # Record metrics
        PREDICTION_LATENCY.observe(latency)
        PREDICTION_OUTPUT.labels(prediction_class=str(int(prediction[0]))).inc()
        PREDICTION_CONFIDENCE.observe(float(confidence))
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='200').inc()

        result = {
            'prediction': int(prediction[0]),
            'label': 'Good Quality' if int(prediction[0]) == 1 else 'Standard Quality',
            'confidence': round(float(confidence), 4),
            'latency_ms': round(latency * 1000, 2)
        }

        return jsonify(result)

    except Exception as e:
        ERROR_COUNT.labels(error_type=type(e).__name__).inc()
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='500').inc()
        return jsonify({'error': str(e)}), 500


@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': time.time()
    })


@app.route('/')
def index():
    """Root endpoint dengan informasi API."""
    return jsonify({
        'service': 'Wine Quality ML Prediction API',
        'author': 'I Kadek Rai Pramana',
        'endpoints': {
            '/predict': 'POST - Make wine quality prediction',
            '/metrics': 'GET - Prometheus metrics',
            '/health': 'GET - Health check'
        }
    })


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    load_model()
    port = int(os.getenv('PORT', 5001))
    print(f"\n{'='*50}")
    print(f"Wine Quality ML Server")
    print(f"Running on http://0.0.0.0:{port}")
    print(f"Metrics: http://0.0.0.0:{port}/metrics")
    print(f"Health:  http://0.0.0.0:{port}/health")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
