#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 08:59:55 2023

@author: elianther
"""
import datetime
import ast
import dependencies.pipeline as pipeline

from airflow.models import Variable
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.google.cloud.operators.pubsub import (
    PubSubCreateSubscriptionOperator,
    PubSubPullOperator
)

# %% STATIC ENVIRONMENT
PROJECT_ID = Variable.get('PROJECT_ID_secret')
TOPIC_ID = Variable.get('TOPIC_ID')
SUBSCRIPTION = Variable.get('SUBSCRIPTION_ID')
# %% PYTHON CALLABLES


def _handle_messages(pulled_messages, context):

    # Order messages from most recent to oldest
    messages = {datetime.datetime.strptime(m.message.ordering_key,
                                           "%Y-%m-%d %H:%M:%S"):
                m.message.data.decode('utf-8')
                for idx, m in enumerate(pulled_messages)
                }
    if messages:
        print(messages)
        # Retrieve the most recent request
        most_recent_message = messages[sorted(messages, reverse=True)[0]]
        print(most_recent_message)
        return most_recent_message
    else:
        return ''


def _order_dataflow_job(ti, **context):
    date_str = ti.xcom_pull(task_ids='pull_messages_operator')

    dates = ast.literal_eval(date_str)
    pipeline.run(dates['startDate'], dates['endDate'], PROJECT_ID)


def _check_if_messages(ti, **context):
    print(PROJECT_ID)
    if ti.xcom_pull(task_ids='pull_messages_operator'):
        return True
    else:
        return False
# %% MAIN LOGIC


with DAG(dag_id="bicycle-analytics-orchestration",
         start_date=datetime.datetime(2023, 4, 3, 11),
         schedule_interval=datetime.timedelta(hours=12),
         catchup=False,
         max_active_runs=1,
         ):

    start_task = DummyOperator(
        task_id='start_task'
    )

    # If subscription exists, we will use it. If not - create new one
    subscribe_task = PubSubCreateSubscriptionOperator(
        task_id="subscribe_task",
        project_id=PROJECT_ID,
        topic=TOPIC_ID,
        subscription=SUBSCRIPTION
    )

    subscription = subscribe_task.output

    # Process messages using callback function _handle_messages
    pull_messages_operator = PubSubPullOperator(
        task_id="pull_messages_operator",
        ack_messages=True,
        messages_callback=_handle_messages,
        project_id=PROJECT_ID,
        subscription=subscription,
        max_messages=100,
    )

    # Check if we received any messages
    check_if_messages = ShortCircuitOperator(
        task_id="check_if_messages",
        python_callable=_check_if_messages
    )

    order_dataflow_job = PythonOperator(
        task_id="order_dataflow_job",
        python_callable=_order_dataflow_job
    )

    end_task = DummyOperator(
        task_id='end_task'
    )

    start_task >> subscribe_task >> pull_messages_operator
    pull_messages_operator >> check_if_messages >> order_dataflow_job
    order_dataflow_job >> end_task
