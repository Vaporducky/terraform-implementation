#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 13:34:29 2023

@author: elianther
"""

import random

months = ['01', '02', '03', '04', '05',
          '06', '07', '08', '09', '10', '11', '12']
quarters = [f"20{year}-{month}-{day}"
            for year in range(13, 24)
            for month in months
            for day in ['01', '15']]

values = [(quarter, round(random.random() * 1.1, 2)) for quarter in quarters]

with open('../../architecture/BigQuery/random_data.sql',
          'w', encoding='utf-8') as file:
    file.write("INSERT INTO <table> VALUES\n")
    file.write("\n".join([f"('{value[0]}',{value[1]})," for value in values]))
