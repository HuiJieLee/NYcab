"""
New York taxicab data 
@author: Hui-Jie Lee
"""

import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from datetime import datetime
import math

# Read data
data = pd.read_csv('trip_data_3.csv', parse_dates = [5,6], skipinitialspace = True)
fare = pd.read_csv('trip_fare_3.csv', parse_dates = [3], skipinitialspace = True)

# for fun
payment_count = fare['payment_type'].value_counts() # CRD, CSH, NOC, DIS, UNK
vendor_id_count = data['vendor_id'].value_counts() # CMT, VTS
rate_code_count = data['rate_code'].value_counts() # 0-9, 17, 210
passenager_count_d = data['passenger_count'].value_counts() # 0-7, 9, 255

# Merge data
cab = pd.merge(data, fare, 'inner')
cab.info() # 15749228

# Remove bad data 
# 1. Remove passenger_count = 0 or > 6
cab = cab[(cab.passenger_count > 0) & (cab.passenger_count < 7) ] # 15748793
# 2. Remove trip_time_in_secs < 10 and trip_distance = 0
cab = cab[(cab.trip_time_in_secs >= 10) & (cab.trip_distance > 0)] # 15650651
# 3. Remove pickup_longitude < -75 or > -70
cab = cab[(cab.pickup_longitude >= -75) & (cab.pickup_longitude <= -70)] # 15396673
# 4. Remove pickup_latitude < 39 or > 41
cab = cab[(cab.pickup_latitude >= 39) & (cab.pickup_latitude <= 41)] # 15395687
# 5. Remove dropoff_longitude < -75 or > -70
cab = cab[(cab.dropoff_longitude >= -75) & (cab.dropoff_longitude <= -70)] # 15384526
# 6. Remove dropoff_latitude < 39 or > 41
cab = cab[(cab.dropoff_latitude >= 39) & (cab.dropoff_latitude <= 41)] # 15383177
# 7. Remove unlikely speed > 70
cab = cab[(cab.trip_distance *3600.0/cab.trip_time_in_secs) <= 70] # 15373579

# Payment under $5
payment5 = cab[cab['total_amount'] <=5] 
payment5.shape
payment5_count = payment5['payment_type'].value_counts()
payment5_count.astype(float)/len(payment5)   

# Payment above $50
payment50 = cab[cab['total_amount'] >= 50] 
payment50.shape
payment50_count = payment50['payment_type'].value_counts()
payment50_count.astype(float)/len(payment50)  

# Mean fare per minute driven
(cab['fare_amount']*60.0/cab['trip_time_in_secs']).mean()

# Median fare per mile driven
(cab['fare_amount']/ cab['trip_distance']).median()

# 95 percentile of the taxi's average driving speed in miles per hour
speed = cab['trip_distance']*3600.0/cab['trip_time_in_secs']
np.percentile(speed, 95)

# Define great_circle distance
def distance(df):
    lat1 = df['pickup_latitude']   
    lon1 = df['pickup_longitude']
    lat2 = df['pickup_latitude']
    lon2 = df['pickup_longitude']
    radius = 3959 # miles
 
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
 
    return d

# Calculate straight distance between pickup and dropoff location
straight_distance = cab.apply(distance, axis = 1)
# Average ratio of the distance b/w the pickup and dropoff and the distance driven
(straight_distance / cab.trip_distance).mean()

# Find pickup location near JFK
nearJFK = cab[(cab.pickup_longitude >= -73.8) & (cab.pickup_longitude <= -73.7) & (cab.pickup_latitude >= 40.64) & (cab.pickup_latitude <= 40.65)]
# Find average tip from JFK
nearJFK.tip_amount.mean()

# Calculate revenue for each taxi driver
revenue = cab.groupby(by = ['hack_license'])['total_amount'].sum()
# Find the median of the revenue
revenue.median()

