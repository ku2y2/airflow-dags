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
    'hello_world_dag',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['demo'],
)

def print_hello():
    print("Hello from Airflow 3!")
    print("This is a demo DAG running in Minikube")
    return "Hello World!"

hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

bash_hello = BashOperator(
    task_id='bash_hello',
    bash_command='echo "Hello from Bash operator!"',
    dag=dag,
)

# Set task dependencies
hello_task >> bash_hello