from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dbt_example_dag',
    default_args=default_args,
    description='A DAG that runs dbt models',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['dbt', 'transformation'],
)

def create_database():
    import mysql.connector

    config = {
        'user': 'airflow',
        'password': 'airflow123',
        'host': 'mysql-service.default.svc.cluster.local',
        'port': 3306,
        'database': 'airflow'
    }

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Create dbt_dev database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS dbt_dev")
    conn.commit()

    cursor.close()
    conn.close()

    print("Database dbt_dev created successfully!")

create_db_task = PythonOperator(
    task_id='create_dbt_database',
    python_callable=create_database,
    dag=dag,
)

# dbt debug to test connection
dbt_debug = BashOperator(
    task_id='dbt_debug',
    bash_command='cd /opt/airflow/dags/dbt && dbt debug --profiles-dir .',
    dag=dag,
)

# dbt run to execute models
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/airflow/dags/dbt && dbt run --profiles-dir .',
    dag=dag,
)

# dbt test to run tests
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /opt/airflow/dags/dbt && dbt test --profiles-dir .',
    dag=dag,
)

# Set task dependencies
dbt_debug >> dbt_run >> dbt_test