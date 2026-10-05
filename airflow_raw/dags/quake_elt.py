from airflow.decorators import dag, task
from datetime import datetime, timedelta
import subprocess

default_args = {
    "retries": 2,                       #retry count for tasks
    "retry_delay": timedelta(minutes=5), # retry delay for tasks
}

@dag(
    dag_id="quake_elt",
    schedule="@hourly",
    start_date=datetime(2026, 10, 1),
    catchup=False,
    default_args=default_args,
)
def quake_elt():

    @task
    def extract():
        subprocess.run(
            ["python", "/opt/airflow/include/scripts/fetch_quakes.py"],
            cwd="/opt/airflow/include",
            check=True
        )

    @task
    def load():
        subprocess.run(
            ["python", "/opt/airflow/include/scripts/connect_db.py"],
            cwd="/opt/airflow/include",
            check=True
        )

    @task(retries=0)                  # thing to note: retries=0 for this task, as we don't want to retry dbt run/test if it fails 
    def transform():
        import os

        profile_content = """
    shaky_isles:
    outputs:
        dev:
        type: duckdb
        path: ../quakes.duckdb
        threads: 1
    target: dev
    """
        os.makedirs(os.path.expanduser("~/.dbt"), exist_ok=True)
        with open(os.path.expanduser("~/.dbt/profiles.yml"), "w") as f:
            f.write(profile_content)

        subprocess.run(["dbt", "run"], cwd="/opt/airflow/include/quake_dbt", check=True)
        subprocess.run(["dbt", "test"], cwd="/opt/airflow/include/quake_dbt", check=True)
        extract() >> load() >> transform()

quake_elt()