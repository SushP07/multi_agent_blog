import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# --- ROBUST FIXED PATH INJECTION ---
# Locates the absolute path of MULTI_AGENT_BLOG root relative to this file's position
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# -----------------------------------

from src.pipeline import DigestPipeline

default_args = {
    'owner': 'Sushrut Pakhale',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def run_pipeline_via_airflow():
    """Airflow execution task that calls your existing pipeline class directly."""
    pipeline = DigestPipeline(output_dir="digests")
    pipeline.run()

with DAG(
    'realtime_macro_sentiment_pipeline',
    default_args=default_args,
    description='Automated T-1 macro ingestion and sentiment evaluation pipeline',
    schedule_interval='0 6 * * *',
    catchup=False,
) as dag:

    execute_pipeline_task = PythonOperator(
        task_id='ingest_and_analyze_macro_data',
        python_callable=run_pipeline_via_airflow,
    )

    execute_pipeline_task