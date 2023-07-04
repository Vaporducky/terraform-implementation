#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 11:31:26 2023

@author: elianther
"""

import requests
import json
import os
import argparse

from datetime import datetime

# =============================================================================
# MAIN LOGIC
# =============================================================================


def request_identity_token():
    """
    Retrieve authorization token to perform an authorized call to endpoint
    Returns
    -------
    str
        Authorization token.
    """
    stream = os.popen('gcloud auth print-identity-token')
    token = stream.read()

    return token.strip()


def send_parameters(start_date, end_date):
    """
    Parameters
    ----------
    start_date : str
        Query start date parameter
    end_date : TYPE
        Query end date parameter

    Returns
    -------
    None.
    """
    url = os.getenv('BICYCLE_ANALYTICS_PUBLISH_PARAMETERS_URL')

    data = {
        'startDate': start_date,
        'endDate': end_date,
        'projectID': os.getenv('PROJECT_ID'),
        'topicID': os.getenv('TOPIC_ID')
    }
    token = request_identity_token()

    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain', 'authorization': f'bearer {token}'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--start_date",
                        help="Start date parameter to be used in BQ query",
                        required=True)
    parser.add_argument("--end_date",
                        help="End date parameter to be used in BQ query",
                        required=True)

    args = parser.parse_args()

    try:
        # Test input dates
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(args.start_date, date_format)
        end_date = datetime.strptime(args.end_date, date_format)

        if end_date < start_date:
            raise ValueError

        send_parameters(args.start_date, args.end_date)
    except ValueError:
        print("Invalid date.\n",
              "Check that your dates follow the format 'yyyy-mm-dd'\n",
              "And that start date is equal or greater than the end date.")
