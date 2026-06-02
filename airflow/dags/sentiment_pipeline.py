from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator

# Inject the root folder into the path so Airflow knows where to find your 'src' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
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
    # This runs the exact same logic your main.py runs locally
    pipeline = DigestPipeline(output_dir="digests")
    pipeline.run()

with DAG(
    'realtime_macro_sentiment_pipeline',
    default_args=default_args,
    description='Automated T-1 macro ingestion and sentiment evaluation pipeline',
    schedule_interval='0 6 * * *',  # Runs daily at 6:00 AM UTC
    catchup=False,
) as dag:

    execute_pipeline_task = PythonOperator(
        task_id='ingest_and_analyze_macro_data',
        python_callable=run_pipeline_via_airflow,
    )

    execute_pipeline_task