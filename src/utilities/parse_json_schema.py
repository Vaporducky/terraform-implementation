#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 19:23:06 2023

@author: elianther
"""


def parse_schema_json(file):
    import json
   # SCHEMA = json.load(open("architecture/BigQuery/on-demand-table-schema.json"))
    SCHEMA = json.load(open(file))
    return ','.join([field['name'] + ':' + field['type'] for field in SCHEMA])
