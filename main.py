import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import traceback

import json

from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from scipy.spatial.distance import pdist, squareform

from models import RideSharingResponse

from flask import Flask
from flask import request

import naive2
import naiveN


app = Flask(__name__, static_url_path='', static_folder='webcontent')

df = ''
MIN_SEATS_SHAREABLE = 4

def parse_dates(x):
    return dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

print ("Reading CSV...")

df = pd.read_csv('2013-11-25-reduced.csv',
 names=["medallion", "hack_license", "vendor_id", "rate_code", "store_and_fwd_flag", "pickup_datetime", "dropoff_datetime", "passenger_count", "trip_time_in_secs", "trip_distance", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude"],
 parse_dates=["pickup_datetime", "dropoff_datetime"],
 index_col="dropoff_datetime",
 date_parser=parse_dates)

print(df.shape)

# remove unused data for GC
df.drop(["medallion", "hack_license"], axis=1, inplace=True)

# remove rides with no dropoff
df = df.query("dropoff_latitude != 0")
df = df.query("dropoff_longitude != 0")

# only want shareable rides, so need seats free
df = df.query("passenger_count <= @MIN_SEATS_SHAREABLE")

df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]

# print(df.dtypes)
print(df.shape)

@app.route("/compute")
def compute():
	print("Handling GET")
	print(request.args['happy_walk_pickup'])
	print(request.args['happy_walk_dropoff'])
	print(request.args['max_delay_time'])
	print(request.args['algorithm'])

	if request.args['algorithm'] == "Naive N":
		return naiveN.compute(df,  float(request.args['happy_walk_pickup']),
	 float(request.args['happy_walk_dropoff']),
	 float(request.args['max_delay_time']))
	elif request.args['algorithm'] == "Naive 2":
		return naive2.compute(df,  float(request.args['happy_walk_pickup']),
	 float(request.args['happy_walk_dropoff']),
	 float(request.args['max_delay_time']))
	else:
		return "{}"

	
	






















# coords = group.as_matrix(columns=['pickup_longitude', 'pickup_latitude'])
# 	db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
# 	cluster_labels = db.labels_
# 	num_clusters = len(set(cluster_labels))
# 	clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
# 	print('Number of clusters: {}'.format(num_clusters))

# 	centermost_points = clusters.map(get_centermost_point)

# 	lats, lons = zip(*centermost_points)
# 	rs = pd.DataFrame({'lon':lons, 'lat':lats})


# fig, ax = plt.subplots(figsize=[10, 6])
		# rs_scatter = ax.scatter(rs['lon'], rs['lat'], c='#99cc99', edgecolor='None', alpha=0.7, s=120)
		# df_scatter = ax.scatter(group['dropoff_longitude'], group['dropoff_latitude'], c='k', alpha=0.9, s=3)
		# ax.set_title('Full data set vs DBSCAN reduced set')
		# ax.set_xlabel('Longitude')
		# ax.set_ylabel('Latitude')
		# ax.legend([df_scatter, rs_scatter], ['Full set', 'Reduced set'], loc='upper right')
		# plt.show()

