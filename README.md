# 🫀 Membangun Sistem Machine Learning

> Submission Proyek Akhir Kelas **Membangun Sistem Machine Learning** — [Dicoding](https://www.dicoding.com/)

**Dataset:** [Heart Disease (Cleveland)](https://archive.ics.uci.edu/ml/datasets/heart+disease) — UCI ML Repository

---

## 📋 Ringkasan Proyek

Proyek ini mengimplementasikan **end-to-end Machine Learning Operations (MLOps)** pipeline untuk klasifikasi penyakit jantung (Heart Disease), mencakup:

1. **Eksperimen & Preprocessing** — EDA, data cleaning, feature engineering
2. **Model Training** — MLflow Tracking dengan hyperparameter tuning
3. **CI/CD Pipeline** — GitHub Actions + MLflow Project untuk automated training
4. **Monitoring & Logging** — Prometheus metrics + Grafana dashboard & alerting

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Eksperimen    │────▶│  Model Building  │────▶│   Workflow CI   │
│   (Notebook)    │     │    (MLflow)      │     │ (GitHub Actions)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   Monitoring &   │
                        │     Logging      │
                        │ (Prometheus +    │
                        │    Grafana)      │
                        └──────────────────┘
```

## 📁 Struktur Submission

```
SMSML_I-Kadek-Rai-Pramana/
├── Eksperimen_SML_I-Kadek-Rai-Pramana.txt  # URL repo eksperimen
├── Workflow-CI.txt                          # URL repo CI
│
├── Membangun_model/
│   ├── modelling.py                         # Basic: Autolog MLflow
│   ├── modelling_tuning.py                  # Skilled: GridSearchCV + Manual Logging
│   ├── requirements.txt
│   ├── screenshoot_dashboard.jpg
│   ├── screenshoot_artifak.jpg
│   └── heart_disease_preprocessing/         # Dataset hasil preprocessing
│
└── Monitoring dan Logging/
    ├── 1.bukti_serving.png
    ├── 2.prometheus.yml
    ├── 3.prometheus_exporter.py              # Flask API + 10 Prometheus metrics
    ├── 7.Inference.py                        # Traffic generator
    ├── 4.bukti monitoring Prometheus/        # 5 screenshot Prometheus
    ├── 5.bukti monitoring Grafana/           # 3 screenshot Grafana
    ├── 6.bukti alerting Grafana/             # Rules + Notifikasi
    └── heart_disease_preprocessing/
```

## 🔗 Repository Terkait

| Repository | Deskripsi |
|------------|-----------|
| [Eksperimen_SML_I-Kadek-Rai-Pramana](https://github.com/rai-pramana/Eksperimen_SML_I-Kadek-Rai-Pramana) | Notebook eksperimen + automated preprocessing (GitHub Actions) |
| [DC-Workflow-CI](https://github.com/rai-pramana/DC-Workflow-CI) | MLflow Project + CI pipeline dengan `mlflow run` (GitHub Actions) |

## 🎯 Pencapaian per Kriteria

| Kriteria | Level | Poin | Detail |
|----------|-------|------|--------|
| 1. Eksperimen | **Advance** | 4/4 | Notebook + `automate.py` + GitHub Actions workflow |
| 2. Model Building | **Skilled** | 3/4 | Autolog + GridSearchCV tuning + 5 artifacts (manual logging) |
| 3. Workflow CI | **Skilled** | 3/4 | MLflow Project + `mlflow run` + artifact upload ke GitHub |
| 4. Monitoring | **Skilled** | 3/4 | Serving + 5 Prometheus metrics + Grafana dashboard `rai_pramana` + 1 alerting |
| **Total** | | **13/16** | |

## 🧪 Model Performance (Heart Disease Classification)

| Metric | Basic (Autolog) | Skilled (Tuning) |
|--------|----------------|-----------------|
| Accuracy | 82.46% | **87.72%** |
| Precision | — | 87.50% |
| Recall | — | 84.00% |
| F1 Score | — | 85.71% |
| ROC AUC | — | **91.63%** |
| Method | Random Forest | GridSearchCV (108 candidates, 5-fold CV) |

## 🛠️ Tech Stack

- **Python** 3.11
- **MLflow** 2.19.0 — Tracking & MLflow Project
- **Scikit-learn** — Random Forest Classifier
- **Prometheus** — Custom metrics exporter (10 metrik)
- **Grafana** — Dashboard (`rai_pramana`) & alerting
- **GitHub Actions** — CI/CD pipeline
- **Flask** — Model serving API (port 5001)

## 🚀 Quick Start

### 1. Jalankan MLflow Tracking Server
```bash
mlflow server --host 127.0.0.1 --port 5000
```

### 2. Train Model
```bash
cd SMSML_I-Kadek-Rai-Pramana/Membangun_model/
python modelling.py            # Basic (autolog)
python modelling_tuning.py     # Skilled (manual logging + tuning)
```

### 3. Jalankan Model Server + Monitoring
```bash
cd SMSML_I-Kadek-Rai-Pramana/Monitoring\ dan\ Logging/
python 3.prometheus_exporter.py   # Flask API + Prometheus metrics (port 5001)

# Di terminal lain:
./prometheus --config.file=2.prometheus.yml   # Port 9090
./grafana-server                               # Port 3000
python 7.Inference.py                          # Generate traffic
```

### 4. CI/CD — Training Otomatis
```bash
# Workflow-CI menggunakan mlflow run untuk menjalankan MLProject:
mlflow run MLProject/ -P n_estimators=100 -P max_depth=10 --env-manager local
```

---

<p align="center">
  <i>Submission untuk kelas Membangun Sistem Machine Learning — Dicoding</i>
</p>
