#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 11:08:44 2023

@author: elianther
"""

import json
import os

from datetime import datetime
from google.cloud import pubsub_v1


# =============================================================================
# STATIC ENVIRONMENT
# =============================================================================
PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_ID = os.getenv('TOPIC_ID')
# =============================================================================
# MAIN LOGIC
# =============================================================================


def parse_request_json(request):
    """
    Parse, prepare and encode message from the JSON payload.
    Expected request:
        {startDate: date_value1, endDate: date_value2}
    """
    data = request.data

    if not data:
        print("Request data: `request.data` is empty.")
        return ("request.data is empty", 400)

    data_json = json.loads(data)

    start_date = data_json['startDate']
    end_date = data_json['endDate']
    PROJECT_ID = data_json['projectID']
    TOPIC_ID = data_json['topicID']

    message_json = json.dumps({
        "startDate": start_date,
        "endDate": end_date
    })

    return message_json.encode('utf-8'), PROJECT_ID, TOPIC_ID


def publish_parameters(request):
    """

    Parameters
    ----------
    request : str
        JSON payload.

    Returns
    -------
    str
        Description of the published message.
    int
        HTTP status code.

    """
    # Encode message from JSON payload

    byte_message, PROJECT_ID, TOPIC_ID = parse_request_json(request)

    # Since we're sending message with an ordering, we require to enable this
    # option from the client itself
    with pubsub_v1.PublisherClient(
            publisher_options=pubsub_v1.types.PublisherOptions(
                enable_message_ordering=True)
    ) as publisher:

        topic_path = publisher.topic_path(
            PROJECT_ID, TOPIC_ID)  # Create topic path
        # Publish message
        try:
            future = publisher.publish(topic_path,
                                       data=byte_message,
                                       ordering_key=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )
            print(f"Message id: {future.result()}")
            return (f"Message ID: {future.result()}\nPublished to: {topic_path}",
                    200)
        except Exception as exception:
            print("ERROR:", exception)
