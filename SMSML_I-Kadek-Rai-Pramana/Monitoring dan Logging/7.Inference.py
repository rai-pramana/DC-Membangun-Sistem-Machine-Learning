"""
Inference Script for Wine Quality ML Model
============================================
Script ini mengirimkan request prediksi ke model server
untuk testing dan demonstrasi inference.

Author: I Kadek Rai Pramana
"""

import requests
import json
import time
import random


# Base URL model server
BASE_URL = "http://localhost:5001"


def check_health():
    """Cek apakah model server berjalan."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.json()}")
        return response.json().get('status') == 'healthy'
    except requests.ConnectionError:
        print("[ERROR] Cannot connect to model server. Make sure it's running.")
        return False


def predict_single(sample: dict):
    """Kirim satu prediksi ke model server."""
    response = requests.post(
        f"{BASE_URL}/predict",
        json=sample,
        headers={'Content-Type': 'application/json'}
    )
    return response.json()


def run_batch_inference(n_samples: int = 20):
    """
    Jalankan batch inference untuk menghasilkan traffic
    yang bisa dimonitor oleh Prometheus dan Grafana.
    """
    # Sample data wine quality (berbagai kualitas)
    sample_wines = [
        {
            "fixed acidity": 7.4, "volatile acidity": 0.70, "citric acid": 0.00,
            "residual sugar": 1.9, "chlorides": 0.076, "free sulfur dioxide": 11.0,
            "total sulfur dioxide": 34.0, "density": 0.9978, "pH": 3.51,
            "sulphates": 0.56, "alcohol": 9.4
        },
        {
            "fixed acidity": 7.8, "volatile acidity": 0.88, "citric acid": 0.00,
            "residual sugar": 2.6, "chlorides": 0.098, "free sulfur dioxide": 25.0,
            "total sulfur dioxide": 67.0, "density": 0.9968, "pH": 3.20,
            "sulphates": 0.68, "alcohol": 9.8
        },
        {
            "fixed acidity": 11.2, "volatile acidity": 0.28, "citric acid": 0.56,
            "residual sugar": 1.9, "chlorides": 0.075, "free sulfur dioxide": 17.0,
            "total sulfur dioxide": 60.0, "density": 0.9980, "pH": 3.16,
            "sulphates": 0.58, "alcohol": 9.8
        },
        {
            "fixed acidity": 7.4, "volatile acidity": 0.70, "citric acid": 0.00,
            "residual sugar": 1.9, "chlorides": 0.076, "free sulfur dioxide": 11.0,
            "total sulfur dioxide": 34.0, "density": 0.9978, "pH": 3.51,
            "sulphates": 0.56, "alcohol": 12.5
        },
        {
            "fixed acidity": 6.7, "volatile acidity": 0.32, "citric acid": 0.44,
            "residual sugar": 2.4, "chlorides": 0.061, "free sulfur dioxide": 24.0,
            "total sulfur dioxide": 48.0, "density": 0.9949, "pH": 3.28,
            "sulphates": 0.76, "alcohol": 11.8
        },
    ]

    print(f"\n{'='*60}")
    print(f"BATCH INFERENCE - {n_samples} Requests")
    print(f"{'='*60}\n")

    results = []
    for i in range(n_samples):
        # Pilih sample acak dan tambahkan sedikit noise
        base_sample = random.choice(sample_wines).copy()
        for key in base_sample:
            base_sample[key] = round(base_sample[key] * random.uniform(0.9, 1.1), 3)

        try:
            result = predict_single(base_sample)
            results.append(result)
            print(f"  Request {i+1:3d}: Prediction={result.get('label', 'N/A')}, "
                  f"Confidence={result.get('confidence', 'N/A')}, "
                  f"Latency={result.get('latency_ms', 'N/A')}ms")
        except Exception as e:
            print(f"  Request {i+1:3d}: ERROR - {e}")

        # Delay antara request
        time.sleep(random.uniform(0.1, 0.5))

    # Summary
    if results:
        good_count = sum(1 for r in results if r.get('prediction') == 1)
        avg_latency = sum(r.get('latency_ms', 0) for r in results) / len(results)
        print(f"\n{'='*60}")
        print(f"INFERENCE SUMMARY")
        print(f"{'='*60}")
        print(f"  Total Requests:   {len(results)}")
        print(f"  Good Quality:     {good_count} ({good_count/len(results)*100:.1f}%)")
        print(f"  Standard Quality: {len(results)-good_count} ({(len(results)-good_count)/len(results)*100:.1f}%)")
        print(f"  Avg Latency:      {avg_latency:.2f}ms")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    print("Wine Quality ML - Inference Script")
    print("=" * 40)

    if check_health():
        print("\n[INFO] Model server is healthy. Starting inference...\n")
        run_batch_inference(n_samples=30)
    else:
        print("\n[ERROR] Model server is not available.")
        print("Please start the server first:")
        print("  python 3.prometheus_exporter.py")
