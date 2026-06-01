"""
Inference Script - Heart Disease Classification
=================================================
Script untuk melakukan inference ke model server
dan men-generate traffic untuk monitoring.

Author: I Kadek Rai Pramana
"""

import requests
import random
import time
import json

SERVER_URL = "http://localhost:5001"


def generate_heart_disease_sample():
    """Generate random Heart Disease sample data."""
    return [
        round(random.uniform(29, 77), 1),    # age
        random.choice([0, 1]),                 # sex
        random.choice([0, 1, 2, 3]),          # cp (chest pain type)
        round(random.uniform(94, 200), 0),    # trestbps
        round(random.uniform(126, 564), 0),   # chol
        random.choice([0, 1]),                 # fbs
        random.choice([0, 1, 2]),             # restecg
        round(random.uniform(71, 202), 0),    # thalach
        random.choice([0, 1]),                 # exang
        round(random.uniform(0, 6.2), 1),     # oldpeak
        random.choice([0, 1, 2]),             # slope
        random.choice([0, 1, 2, 3]),          # ca
        random.choice([3.0, 6.0, 7.0]),       # thal
    ]


def main():
    """Generate inference traffic."""
    print("=" * 60)
    print("HEART DISEASE INFERENCE TRAFFIC GENERATOR")
    print("=" * 60)

    # Check server health
    try:
        r = requests.get(f"{SERVER_URL}/health", timeout=5)
        health = r.json()
        print(f"\n[INFO] Server status: {health['status']}")
        print(f"[INFO] Model accuracy: {health['model_accuracy']}")
    except Exception as e:
        print(f"[ERROR] Server not reachable: {e}")
        return

    # Generate traffic
    n_requests = 100
    print(f"\n[INFO] Sending {n_requests} inference requests...\n")

    results = {'no_disease': 0, 'has_disease': 0, 'errors': 0}

    for i in range(n_requests):
        try:
            sample = generate_heart_disease_sample()
            payload = {"features": [sample]}

            r = requests.post(f"{SERVER_URL}/predict", json=payload, timeout=10)

            if r.status_code == 200:
                result = r.json()
                label = result['labels'][0]
                results[label] = results.get(label, 0) + 1
                prob = result['probabilities'][0]

                if (i + 1) % 20 == 0:
                    print(f"  [{i+1:3d}/{n_requests}] Prediction: {label} "
                          f"(prob: {max(prob):.3f}) "
                          f"| latency: {result['latency_ms']:.1f}ms")
            else:
                results['errors'] += 1

        except Exception as e:
            results['errors'] += 1

        # Simulate realistic traffic
        time.sleep(random.uniform(0.1, 0.5))

    # Summary
    print(f"\n{'='*60}")
    print("INFERENCE SUMMARY")
    print(f"{'='*60}")
    print(f"  Total requests: {n_requests}")
    print(f"  No Disease:     {results['no_disease']}")
    print(f"  Has Disease:    {results['has_disease']}")
    print(f"  Errors:         {results['errors']}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
