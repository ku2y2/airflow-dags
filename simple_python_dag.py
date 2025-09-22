from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import json

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
    'simple_python_job',
    default_args=default_args,
    description='A simple Python job DAG',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['python', 'demo'],
)

def data_processing_task():
    """
    A simple data processing function
    """
    import random
    import time

    print("Starting data processing job...")

    # Simulate data processing
    data = []
    for i in range(10):
        record = {
            'id': i + 1,
            'name': f'item_{i + 1}',
            'value': random.randint(1, 100),
            'timestamp': datetime.now().isoformat()
        }
        data.append(record)
        time.sleep(0.5)  # Simulate processing time

    print(f"Processed {len(data)} records")
    print("Sample data:", json.dumps(data[:3], indent=2))

    return f"Successfully processed {len(data)} records"

def data_validation_task():
    """
    A simple data validation function
    """
    print("Starting data validation...")

    # Simulate validation checks
    checks = [
        "Data format validation: PASSED",
        "Data completeness check: PASSED",
        "Data consistency check: PASSED",
        "Business rules validation: PASSED"
    ]

    for check in checks:
        print(check)

    print("All validation checks completed successfully!")
    return "Data validation completed"

def generate_report_task():
    """
    Generate a simple report
    """
    print("Generating report...")

    report = {
        'execution_date': datetime.now().isoformat(),
        'total_records_processed': 10,
        'validation_status': 'PASSED',
        'execution_time': '5.2 seconds',
        'status': 'SUCCESS'
    }

    print("Report generated:")
    print(json.dumps(report, indent=2))

    return "Report generation completed"

# Define tasks
process_data = PythonOperator(
    task_id='process_data',
    python_callable=data_processing_task,
    dag=dag,
)

validate_data = PythonOperator(
    task_id='validate_data',
    python_callable=data_validation_task,
    dag=dag,
)

generate_report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report_task,
    dag=dag,
)

# Set task dependencies
process_data >> validate_data >> generate_report