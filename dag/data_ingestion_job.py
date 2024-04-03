import os
import pandas as pd
import random
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import datetime
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.exc import SQLAlchemyError
import great_expectations as ge
import requests
import json
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.dataset.pandas_dataset import PandasDataset
from great_expectations.data_context.data_context import DataContext
from airflow.operators.python import BranchPythonOperator
from sqlalchemy import String
from sqlalchemy import DateTime
import hashlib
from great_expectations.data_context import DataContext
from great_expectations.data_context import BaseDataContext

# Define the global path variable
RAW_DATA_PATH = '/home/sachin/DSP/airflow-spike-master/input_data/raw-data'
# Initialize the storage paths for good and bad data
good_data_path = os.path.join('/home/sachin/DSP/airflow-spike-master/output_data', 'good_data')
bad_data_path = os.path.join('/home/sachin/DSP/airflow-spike-master/output_data', 'bad_data')

def read_data(**kwargs):

    files = os.listdir(RAW_DATA_PATH)
    selected_file = random.choice(files)
    file_path = os.path.join(RAW_DATA_PATH, selected_file)
    #file_path =  '/home/sachin/DSP/airflow-spike-master/input_data/raw-data/data_chunk_52.csv'
    print("file_path in   read_datais ",file_path)
    kwargs['ti'].xcom_push(key='file_path', value=file_path)
    

def validate_data(**kwargs):
    file_path = kwargs['ti'].xcom_pull(key='file_path', task_ids='read_data')
    print("file_path in   validate_data is  ",file_path)

    df = pd.read_csv(file_path)
    ge_directory = '/home/sachin/DSP/car_price_prediction/gx/'
    context = DataContext(context_root_dir=ge_directory)
    expectation_suite_name = "my_ex"

    expectation_suite = context.get_expectation_suite(expectation_suite_name)

    ge_df = PandasDataset(df, expectation_suite=expectation_suite)

    validation_results = ge_df.validate(expectation_suite=expectation_suite)

    kwargs['ti'].xcom_push(key='validation_results', value=validation_results)
    if validation_results['success']:
        print(file_path,' is a good data')
        kwargs['ti'].xcom_push(key='data_quality', value='good_data')
    else:
        print(file_path,' is a bad data')
        kwargs['ti'].xcom_push(key='data_quality', value='bad_data')
    pass


def decide_which_path(**kwargs):
    ti = kwargs['ti']
    data_quality = ti.xcom_pull(task_ids='validate_data', key='data_quality')
    
    if data_quality == 'good_data':
        return 'save_file'
    else:
        return ['send_alerts', 'save_data_errors','save_file']



def send_alerts(**kwargs):
    
    validation_results = kwargs['ti'].xcom_pull(key='validation_results', task_ids='validate_data')
    file_path = kwargs['ti'].xcom_pull(key='file_path', task_ids='read_data')

    total_rows = len(validation_results["results"])
    failed_rows = len([result for result in validation_results["results"] if not result["success"]])
    
    ge_directory = '/home/sachin/DSP/car_price_prediction/gx/'
    context = DataContext(context_root_dir=ge_directory)
    context.build_data_docs()

    ge_directory = '/home/sachin/DSP/car_price_prediction/gx/'
    data_context = DataContext(ge_directory)

    data_context.build_data_docs()
    data_docs_url = data_context.get_docs_sites_urls()[0]['site_url']
    print(f"Data Docs report available at: {data_docs_url}")

    teams_webhook_url = "https://epitafr.webhook.office.com/webhookb2/66c8b7ae-6477-4603-9a5b-49d5f2191a91@3534b3d7-316c-4bc9-9ede-605c860f49d2/IncomingWebhook/f76d2dd16d7e44189ed49093915d8360/4981d105-4c57-4ae4-ac72-2623b4a8b6b8"
    headers = {'Content-Type': 'application/json'}

    data_docs_url = "http://34.125.23.232:8000/local_site/index.html"

    if failed_rows > 5:
        criticality = 'high'
    elif failed_rows > 3:
        criticality = 'medium'
    else:
        criticality = 'low'

    alert_message = {
        "text": f"Data Problem Alert:\nCriticality: {criticality}\nSummary: {failed_rows} rows failed validation.\nCheck the detailed report here: {data_docs_url}"
    }

    try:
        response = requests.post(teams_webhook_url, headers=headers, json=alert_message)
        if response.status_code == 200:
            print("Alert sent to Teams successfully.")
        else:
            print(f"Failed to send alert to Teams. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending alert to Teams: {e}")


def save_file(**kwargs):
    file_path = kwargs['ti'].xcom_pull(key='file_path', task_ids='read_data')
    data_quality = kwargs['ti'].xcom_pull(key='data_quality', task_ids='validate_data')
    df = pd.read_csv(file_path)

    if data_quality == 'good_data':
        df.to_csv(os.path.join(good_data_path, os.path.basename(file_path)), index=False)
    else:
        df.to_csv(os.path.join(bad_data_path, os.path.basename(file_path)), index=False)

    os.remove(file_path)

def save_data_errors(**kwargs):

    validation_results = kwargs['ti'].xcom_pull(key='validation_results', task_ids='validate_data')
    file_path = kwargs['ti'].xcom_pull(key='file_path', task_ids='read_data')
    total_rows = len(validation_results["results"])
    failed_rows = len([result for result in validation_results["results"] if not result["success"]])

    db_connection_string = "postgresql://car:password@34.125.23.232/carprice"
    engine = create_engine(db_connection_string)

    metadata = MetaData()

    data_quality_table = Table(
        'data_quality_statistics',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('total_rows', Integer),
        Column('failed_rows', Integer),
        Column('timestamp', DateTime),
        Column('file_path', String(500)),
    )

    metadata.create_all(engine)

    try:
        with engine.connect() as connection:
            insert_query = data_quality_table.insert().values(
                total_rows=total_rows,
                failed_rows=failed_rows,
                timestamp=datetime.datetime.now(),
                file_path=file_path,
            )
            connection.execute(insert_query)
            print("Data quality statistics saved to the database.")
    except SQLAlchemyError as e:
        print(f"Error saving data quality statistics to the database: {e}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

dag = DAG(
    'data_ingestion_pipelines',
    default_args=default_args,
    schedule='@daily',
    catchup=False
)


read_data_task = PythonOperator(
    task_id='read_data',
    python_callable=read_data,
    provide_context=True,
    dag=dag,
)

validate_data_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)
branch_task = BranchPythonOperator(
    task_id='branch_based_on_validation',
    python_callable=decide_which_path,
    provide_context=True,
    dag=dag,
)

send_alerts_task = PythonOperator(
    task_id='send_alerts',
    python_callable=send_alerts,
    provide_context=True,
    dag=dag,
    trigger_rule='all_success',
)

save_file_task = PythonOperator(
    task_id='save_file',
    python_callable=save_file,
    provide_context=True,
    dag=dag,
)

save_data_errors_task = PythonOperator(
    task_id='save_data_errors',
    python_callable=save_data_errors,
    provide_context=True,
    dag=dag,
    trigger_rule='all_success',
)

read_data_task >> validate_data_task >>  branch_task
branch_task >> save_file_task
branch_task >> send_alerts_task
branch_task >> save_data_errors_task