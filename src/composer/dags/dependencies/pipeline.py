#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:21:28 2023

@author: elianther
"""
import apache_beam as beam
import logging
import traceback

import datetime
from apache_beam.options.pipeline_options import PipelineOptions

# =============================================================================
# STATIC ENVIRONMENT
# =============================================================================
SCHEMA = 'duration_minutes:INTEGER,trip_cost:FLOAT,bike_id:STRING,start_time:TIMESTAMP,end_time:TIMESTAMP,start_station_id:INTEGER,start_station_name:STRING,end_station_id:STRING,end_station_name:STRING'
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
FORMAT = '%Y-%m-%d %H:%M:%S UTC'
# =============================================================================
# FUNCTIONS
# =============================================================================


def _broadcast_join(element, side_input):
    """
    Parameters
    ----------
    element : PCollection
        Result from fact query
    side_input : PCollection
        Result from dimension query
    Returns
    -------
    result : PCollection
        Joined data on 'quarter_id' key.

    """
    result = element.copy()
    try:
        result.update(side_input[element['quarter_id']])
    except KeyError as err:
        traceback.print_exc()
        logging.error("Quarter ID not found: %s", err)

    return result


def _remove_quarter_id_and_cost(element):
    element.pop('quarter_id')
    element.pop('cost')
    return element


def _determine_trip_cost(element):
    result = element.copy()
    try:
        result.update({'trip_cost':
                       round(element['cost'] * element['duration_minutes'], 2)}
                      )
    except KeyError as err:
        traceback.print_exc()
        logging.error(err)

    return result


def _determine_end_time(element):
    result = element.copy()
    try:
        difference = datetime.timedelta(minutes=element['duration_minutes'])
        end_time = element['start_time'] + difference
        result.update({'end_time': end_time})
    except Exception as err:
        traceback.print_exc()
        logging.error("Parsing not correct: %s", err)

    return result
# =============================================================================
# MAIN LOGIC
# =============================================================================
# We assume the table {PROJECT_ID}.bicycle_dataset.bike_trips exists


def run(start_date, end_date, PROJECT_ID):
    logging.getLogger().setLevel(logging.INFO)

    FACT_QUERY = f"""SELECT
      DATE(DATE_TRUNC(start_time, QUARTER)) AS quarter_id,
      duration_minutes,
      bikeid AS bike_id,
      start_time,
      start_station_id,
      start_station_name,
      end_station_id,
      end_station_name
    FROM
      `{PROJECT_ID}.bicycle_dataset.bike_trips_fact`
    WHERE
      DATE(start_time) BETWEEN DATE('{start_date}') AND DATE('{end_date}')
    """
    DIM_QUERY = f"""SELECT
      quarter as quarter_id,
      cost
    FROM
      `{PROJECT_ID}.bicycle_dataset.quarter_cost_dim`
    """
    # %% Pipeline

    beam_options = PipelineOptions(
        # Use DirectRunner to test locally
        # DataflowRunner to initialize Dataflow
        runner='DirectRunner',
        temp_location=f'gs://{PROJECT_ID}-ingestion/temp/',
        staging_location=f'gs://{PROJECT_ID}-ingestion/stg/',
        project=PROJECT_ID,
        job_name=f'{PROJECT_ID}-bicycle-analytics-{TODAY}',
        region='us-central1',
        save_main_session=True
    )

    # Defining the pipeline in this format, we decouple the service once it
    # has been ordered in Dataflow
    pipeline = beam.Pipeline(options=beam_options)
    side_input = (
        pipeline
        | "Read dimension table from BigQuery" >> beam.io.ReadFromBigQuery(
            query=DIM_QUERY,
            use_standard_sql=True)
        # Create join key on the PCollection (value: {...})
        | "Create join key" >> beam.Map(lambda x: (x['quarter_id'], x))
    )
    # Initiate main pipeline
    (
     pipeline
     | f"Read from BigQuery using range: {start_date} - {end_date}"
     >> beam.io.ReadFromBigQuery(
         query=FACT_QUERY,
         use_standard_sql=True
     )
     | "Do a broadcast join" >> beam.Map(_broadcast_join,
                                         beam.pvalue.AsDict(side_input))
     | "Determine cost per trip" >> beam.Map(_determine_trip_cost)

     | "Determine end time" >> beam.Map(_determine_end_time)
     | "Remove unused keys" >> beam.Map(_remove_quarter_id_and_cost)
     | "Write to BigQuery" >> beam.io.WriteToBigQuery(
         f'{PROJECT_ID}:bicycle_analytic.on_demand_report',
         schema=SCHEMA,
         write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
         create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER
     )
    )
    pipeline.run().wait_until_finish()
