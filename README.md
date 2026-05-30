# 🍷 Membangun Sistem Machine Learning

> Submission Proyek Akhir Kelas **Membangun Sistem Machine Learning** — [Dicoding](https://www.dicoding.com/)

**Nama:** I Kadek Rai Pramana  
**Username Dicoding:** `rai_pramana`  
**Dataset:** [Wine Quality (Red)](https://archive.ics.uci.edu/ml/datasets/wine+quality) — UCI ML Repository

---

## 📋 Ringkasan Proyek

Proyek ini mengimplementasikan **end-to-end Machine Learning Operations (MLOps)** pipeline untuk klasifikasi kualitas wine, mencakup:

1. **Eksperimen & Preprocessing** — EDA, data cleaning, feature engineering
2. **Model Training** — MLflow Tracking dengan hyperparameter tuning
3. **CI/CD Pipeline** — GitHub Actions untuk automated training
4. **Monitoring & Logging** — Prometheus metrics + Grafana dashboard

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

## 📁 Struktur Proyek

```
DC-Membangun-Sistem-Machine-Learning/
├── instruction/                          # Instruksi submission Dicoding
│   ├── submission_instruction.md
│   └── Template_Eksperimen_MSML.ipynb
│
├── SMSML_I-Kadek-Rai-Pramana/           # Folder submission utama
│   ├── Eksperimen_SML_I-Kadek-Rai-Pramana.txt
│   ├── Workflow-CI.txt
│   │
│   ├── Membangun_model/
│   │   ├── modelling.py                  # Basic: Autolog MLflow
│   │   ├── modelling_tuning.py           # Skilled: GridSearchCV + Manual Logging
│   │   ├── requirements.txt
│   │   ├── screenshoot_dashboard.jpg
│   │   ├── screenshoot_artifak.jpg
│   │   └── wine_quality_preprocessing/
│   │
│   └── Monitoring dan Logging/
│       ├── 1.bukti_serving.png
│       ├── 2.prometheus.yml
│       ├── 3.prometheus_exporter.py      # Flask API + 10 Prometheus metrics
│       ├── 7.Inference.py                # Traffic generator
│       ├── 4.bukti monitoring Prometheus/
│       ├── 5.bukti monitoring Grafana/
│       ├── 6.bukti alerting Grafana/
│       └── wine_quality_preprocessing/
│
└── SMSML_I-Kadek-Rai-Pramana.zip        # ZIP siap submit
```

## 🔗 Repository Terkait

| Repository | Deskripsi |
|------------|-----------|
| [Eksperimen_SML_I-Kadek-Rai-Pramana](https://github.com/rai-pramana/Eksperimen_SML_I-Kadek-Rai-Pramana) | Notebook eksperimen + automated preprocessing (GitHub Actions) |
| [DC-Workflow-CI](https://github.com/rai-pramana/DC-Workflow-CI) | MLflow Project + CI pipeline (GitHub Actions) |

## 🎯 Pencapaian per Kriteria

| Kriteria | Level | Poin | Detail |
|----------|-------|------|--------|
| 1. Eksperimen | **Advance** | 4/4 | Notebook + automate script + GitHub Actions workflow |
| 2. Model Building | **Skilled** | 3/4 | Autolog + GridSearchCV tuning + 5 artifacts (manual logging) |
| 3. Workflow CI | **Skilled** | 3/4 | MLflow Project + CI pipeline + artifact upload |
| 4. Monitoring | **Skilled** | 3/4 | Serving + 5 Prometheus metrics + Grafana + 1 alerting |
| **Total** | | **13/16** | |

## 🧪 Model Performance

| Metric | Basic (Autolog) | Skilled (Tuning) |
|--------|----------------|-----------------|
| Accuracy | 90.36% | 89.34% |
| F1 Score | — | 0.5238 |
| ROC AUC | — | 0.8514 |
| Method | Random Forest | GridSearchCV (108 candidates) |

## 🛠️ Tech Stack

- **Python** 3.11.9
- **MLflow** 2.19.0
- **Scikit-learn** — Random Forest Classifier
- **Prometheus** — Custom metrics exporter
- **Grafana** — Dashboard & alerting
- **GitHub Actions** — CI/CD pipeline
- **Flask** — Model serving API

## 🚀 Quick Start

### 1. Jalankan Model Server
```bash
cd SMSML_I-Kadek-Rai-Pramana/Monitoring\ dan\ Logging/
python 3.prometheus_exporter.py
```

### 2. Jalankan Prometheus
```bash
# Download dan extract Prometheus
./prometheus --config.file=2.prometheus.yml
```

### 3. Jalankan Grafana
```bash
# Download dan extract Grafana
./grafana-server
# Buka http://localhost:3000, login admin/admin
# Tambah data source Prometheus (http://localhost:9090)
# Buat dashboard dengan nama: rai_pramana
```

### 4. Generate Traffic
```bash
python 7.Inference.py
```

---

<p align="center">
  <i>Dibuat sebagai submission untuk kelas Membangun Sistem Machine Learning di Dicoding</i>
</p>
