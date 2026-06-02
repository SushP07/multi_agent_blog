import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

default_args = {
    'owner': 'Sushrut Pakhale',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def run_isolated_pipeline():
    """This function runs inside a completely isolated Python environment."""
    import os
    import sys
    
    # Dynamic path injection inside the fresh virtual environment context
    # GitHub workspace default root path: /home/runner/work/multi_agent_blog/multi_agent_blog
    PROJECT_ROOT = "/home/runner/work/multi_agent_blog/multi_agent_blog"
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
        
    from src.pipeline import DigestPipeline
    
    print("🚀 Running pipeline within an isolated production environment container...")
    pipeline = DigestPipeline(output_dir="digests")
    result = pipeline.run()
    print(f"Pipeline finished cleanly:\n{result}")

with DAG(
    'realtime_macro_sentiment_pipeline',
    default_args=default_args,
    description='Automated T-1 macro ingestion and sentiment evaluation pipeline via Virtualenv',
    schedule_interval='0 6 * * *',
    catchup=False,
) as dag:

    execute_pipeline_task = PythonVirtualenvOperator(
        task_id='ingest_and_analyze_macro_data',
        python_callable=run_isolated_pipeline,
        # Requirements specifically needed by your AI agent code
        requirements=[
            "feedparser==6.0.11",
            "python-dateutil==2.9.0.post0",
            "agno==1.0.1",
            "google-genai==0.1.1",
            "typing-extensions>=4.10.0" # Keeps google-genai completely satisfied
        ],
        # System env variables to pass down into the isolated execution space
        system_site_packages=False, 
    )

    execute_pipeline_task