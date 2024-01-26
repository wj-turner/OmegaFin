# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.operators.bash_operator import BashOperator
# from datetime import datetime, timedelta
# import psycopg2  # Ensure psycopg2 is installed in your Airflow environment

# # Constants (modify these with your actual credentials and paths)
# DB_NAME = 'forexdb'
# DB_USER = 'forexuser'
# DB_PASSWORD = 'forexpassword'
# DB_HOST = 'postgres'
# CONTAINER_NAME = 'ctrader_hist_data'
# FETCH_SCRIPT_PATH = 'src/GetHistData.py'

# default_args = {
#     'owner': 'airflow',
#     'start_date': datetime(2024, 1, 25),
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'fetch_forex_data',
#     default_args=default_args,
#     description='DAG for fetching forex data',
#     schedule_interval=timedelta(days=1),
# )

# def check_data_gaps():
#     # Establish a connection to the database
#     conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
#     cur = conn.cursor()

#     # SQL query to find data gaps
#     cur.execute("SELECT symbol, start_date, end_date, timeframe FROM time_data_gap WHERE status = 'pending' ORDER BY id LIMIT 1")
#     row = cur.fetchone()

#     # Close the database connection
#     cur.close()
#     conn.close()

#     return row

# def build_fetch_command(params):
#     return f"docker exec {CONTAINER_NAME} python {FETCH_SCRIPT_PATH} --symbol '{params['symbol']}' --fromTimestamp '{params['start_date']}' --toTimestamp '{params['end_date']}' --period '{params['timeframe']}'"

# check_data_gaps_task = PythonOperator(
#     task_id='check_data_gaps',
#     python_callable=check_data_gaps,
#     dag=dag,
# )

# def execute_fetch(**kwargs):
#     # Retrieve data gaps from the previous task
#     data_gap = kwargs['ti'].xcom_pull(task_ids='check_data_gaps')

#     if data_gap:
#         symbol, start_date, end_date, timeframe = data_gap
        
#         fetch_cmd = build_fetch_command({
#             'symbol': symbol,
#             'start_date': start_date,
#             'end_date': end_date,
#             'timeframe': timeframe
#         })

#         # Execute the fetch command here or set it to a BashOperator
#         # Example: Using BashOperator
#         fetch_data_task = BashOperator(
#             task_id='fetch_data',
#             bash_command=fetch_cmd,
#             dag=dag,
#         )
#         fetch_data_task.execute(context=kwargs)


# execute_fetch_task = PythonOperator(
#     task_id='execute_fetch',
#     python_callable=execute_fetch,
#     provide_context=True,
#     dag=dag,
# )

# check_data_gaps_task >> execute_fetch_task

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta
import psycopg2

# Constants
DB_NAME = 'forexdb'
DB_USER = 'forexuser'
DB_PASSWORD = 'forexpassword'
DB_HOST = 'postgres'
DOCKER_IMAGE = 'ctrader_hist_data'  # Replace with your Docker image name
FETCH_SCRIPT_PATH = '/src/GetHistData.py'  # Adjust path as needed

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 25),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_forex_data',
    default_args=default_args,
    description='DAG for fetching forex data',
    schedule_interval=timedelta(days=1),
)

def check_data_gaps():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()

    # SQL query to find data gaps
    cur.execute("SELECT symbol, start_date, end_date, timeframe FROM time_data_gap WHERE status = 'pending' ORDER BY id LIMIT 1")
    row = cur.fetchone()

    # Close the database connection
    cur.close()
    conn.close()

    return row

def execute_fetch(**kwargs):
    data_gap = kwargs['ti'].xcom_pull(task_ids='check_data_gaps')
    if data_gap:
        symbol, start_date, end_date, timeframe = data_gap
        fetch_data_task = DockerOperator(
            task_id='fetch_data',
            image=DOCKER_IMAGE,
            api_version='auto',
            auto_remove=True,
            command=f"python {FETCH_SCRIPT_PATH} --symbol '{symbol}' --fromTimestamp '{start_date}' --toTimestamp '{end_date}' --period '{timeframe}'",
            docker_url="unix://var/run/docker.sock",
            network_mode="bridge",
            dag=dag
        )
        fetch_data_task.execute(context=kwargs)

check_data_gaps_task = PythonOperator(
    task_id='check_data_gaps',
    python_callable=check_data_gaps,
    dag=dag,
)

execute_fetch_task = PythonOperator(
    task_id='execute_fetch',
    python_callable=execute_fetch,
    provide_context=True,
    dag=dag,
)

check_data_gaps_task >> execute_fetch_task
