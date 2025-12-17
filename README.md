
# E-commerce Segmentation & Monitoring System

## Overview
This project processes customer data to identify behavioral segments and provides an interactive dashboard for analysis.

## Integration Flow
The system consists of two main components integrated via file-based data exchange:

1.  **Data Pipeline (`src/pipeline`)**:
    *   **Input**: Reads raw customer data from `data/customer_data.csv`.
    *   **Processing**: Uses PySpark for RFM analysis, Feature Engineering, and K-Means Clustering.
    *   **Output**: Saves processed data with segment labels to `output/clustered_output/final_output.csv`.

2.  **Dashboard (`src/dashboard`)**:
    *   **Input**: Reads the processed `final_output.csv`.
    *   **UI**: Streamlit application for visualizing segments, trends, and KPIs.

## Installation
Ensure you have the requirements installed:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Run the Data Pipeline
Execute the Spark pipeline to process data and generate segments:
```bash
python src/pipeline/run_pipeline.py
```
*   Optional arguments: `--input <path>`, `--k <num_clusters>`

### 2. Launch the Dashboard
Start the web interface:
```bash
streamlit run src/dashboard/app.py
```

## Authentication
The dashboard is protected. Use the following credentials:

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| **Admin** | `admin` | `admin` | Full access (System Monitor, Settings) |
| **Analyst** | `analyst` | `analyst` | Analytics views only |

*Note: Credentials are configured in `src/dashboard/utils/auth_config.yaml`.*
