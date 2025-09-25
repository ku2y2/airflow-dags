from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.bash import BashOperator

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
    'dbt_kubernetes_dag',
    default_args=default_args,
    description='A dbt DAG running on KubernetesExecutor',
    schedule_interval=timedelta(hours=6),
    catchup=False,
    tags=['dbt', 'kubernetes', 'data-pipeline'],
)

# dbt deps task
dbt_deps = KubernetesPodOperator(
    task_id='dbt_deps',
    name='dbt-deps',
    namespace='default',
    image='ghcr.io/dbt-labs/dbt-postgres:1.8.0',
    cmds=['/bin/bash', '-c'],
    arguments=[
        '''
        cd /opt/airflow/dbt &&
        dbt deps --profiles-dir /opt/airflow/dbt
        '''
    ],
    volumes=[],
    volume_mounts=[],
    env_vars={
        'DBT_PROFILES_DIR': '/opt/airflow/dbt',
    },
    is_delete_operator_pod=True,
    get_logs=True,
    dag=dag,
)

# dbt run task
dbt_run = KubernetesPodOperator(
    task_id='dbt_run',
    name='dbt-run',
    namespace='default',
    image='ghcr.io/dbt-labs/dbt-postgres:1.8.0',
    cmds=['/bin/bash', '-c'],
    arguments=[
        '''
        cd /opt/airflow/dbt &&
        dbt run --profiles-dir /opt/airflow/dbt --target dev
        '''
    ],
    volumes=[],
    volume_mounts=[],
    env_vars={
        'DBT_PROFILES_DIR': '/opt/airflow/dbt',
    },
    is_delete_operator_pod=True,
    get_logs=True,
    dag=dag,
)

# dbt test task
dbt_test = KubernetesPodOperator(
    task_id='dbt_test',
    name='dbt-test',
    namespace='default',
    image='ghcr.io/dbt-labs/dbt-postgres:1.8.0',
    cmds=['/bin/bash', '-c'],
    arguments=[
        '''
        cd /opt/airflow/dbt &&
        dbt test --profiles-dir /opt/airflow/dbt --target dev
        '''
    ],
    volumes=[],
    volume_mounts=[],
    env_vars={
        'DBT_PROFILES_DIR': '/opt/airflow/dbt',
    },
    is_delete_operator_pod=True,
    get_logs=True,
    dag=dag,
)

# Set task dependencies
dbt_deps >> dbt_run >> dbt_test