from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import psycopg2  # Ensure psycopg2 is installed in your Airflow environment

# Constants (modify these with your actual credentials and paths)
DB_NAME = 'your_database_name'
DB_USER = 'your_database_user'
DB_PASSWORD = 'your_database_password'
DB_HOST = 'your_database_host'
CONTAINER_NAME = 'your_data_fetching_container'
FETCH_SCRIPT_PATH = '/path/to/your/fetch_script.py'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # ... other default args
}

dag = DAG(
    'fetch_forex_data',
    default_args=default_args,
    description='DAG for fetching forex data',
    schedule_interval=timedelta(days=1),
)

def check_data_gaps():
    # Establish a connection to the database
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()

    # SQL query to find data gaps
    cur.execute("SELECT symbol, start_date, end_date, timeframe FROM your_table WHERE status = 'pending'")
    rows = cur.fetchall()

    # Close the database connection
    cur.close()
    conn.close()

    return rows

def build_fetch_command(params):
    return f"docker exec {CONTAINER_NAME} python {FETCH_SCRIPT_PATH} --symbol '{params['symbol']}' --start_date '{params['start_date']}' --end_date '{params['end_date']}' --timeframe '{params['timeframe']}'"

check_data_gaps_task = PythonOperator(
    task_id='check_data_gaps',
    python_callable=check_data_gaps,
    dag=dag,
)

def execute_fetch(**kwargs):
    # Retrieve data gaps from the previous task
    data_gaps = kwargs['ti'].xcom_pull(task_ids='check_data_gaps')

    # Loop over each data gap and execute fetch command
    for gap in data_gaps:
        symbol, start_date, end_date, timeframe = gap
        fetch_cmd = build_fetch_command({
            'symbol': symbol,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'timeframe': timeframe
        })
        fetch_data_task = BashOperator(
            task_id=f'fetch_data_{symbol}_{start_date}_{end_date}',
            bash_command=fetch_cmd,
            dag=dag,
        )
        fetch_data_task.execute(context=kwargs)

execute_fetch_task = PythonOperator(
    task_id='execute_fetch',
    python_callable=execute_fetch,
    provide_context=True,
    dag=dag,
)

check_data_gaps_task >> execute_fetch_task
