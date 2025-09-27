from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

dag = DAG(
    'hello_test_dag',
    default_args=default_args,
    description='A simple test DAG',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['test', 'hello'],
)

def hello_world():
    print("Hello World from Airflow!")
    print("This is a test DAG running successfully!")
    return "Success!"

def print_context(**kwargs):
    print("Task instance:", kwargs['ti'])
    print("Execution date:", kwargs['ds'])
    print("Task ID:", kwargs['task'].task_id)
    return "Context printed!"

hello_task = PythonOperator(
    task_id='hello_world',
    python_callable=hello_world,
    dag=dag,
)

context_task = PythonOperator(
    task_id='print_context',
    python_callable=print_context,
    dag=dag,
)

hello_task >> context_task