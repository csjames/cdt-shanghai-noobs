import pandas as pd
import numpy as np
import json
import traceback

MAX_WAITING_TIME = 10

HAPPY_WALKING_DISTANCE = 0.2

HAPPY_PICKUP_WALKING_DISTANCE = 0.3

kms_per_radian = 6371.0088
epsilon = 1.5 / kms_per_radian

def distance_on_sphere_numpy(coordinate_array):
    """
    Compute a distance matrix of the coordinates using a spherical metric.
    :param coordinate_array: numpy.ndarray with shape (n,2); latitude is in 1st col, longitude in 2nd.
    :returns distance_mat: numpy.ndarray with shape (n, n) containing distance in km between coords.
    """
    # Radius of the earth in km (GRS 80-Ellipsoid)
    EARTH_RADIUS = 6371.007176 

    # Unpacking coordinates
    latitudes = coordinate_array[:, 0]
    longitudes = coordinate_array[:, 1]
    n_pts = coordinate_array.shape[0]

    # Convert latitude and longitude to spherical coordinates in radians.
    degrees_to_radians = np.pi/180.0
    phi_values = (90.0 - latitudes)*degrees_to_radians
    theta_values = longitudes*degrees_to_radians

    # Expand phi_values and theta_values into grids
    theta_1, theta_2 = np.meshgrid(theta_values, theta_values)
    theta_diff_mat = theta_1 - theta_2

    phi_1, phi_2 = np.meshgrid(phi_values, phi_values)

    # Compute spherical distance from spherical coordinates
    angle = (np.sin(phi_1) * np.sin(phi_2) * np.cos(theta_diff_mat) + 
           np.cos(phi_1) * np.cos(phi_2))
    arc = np.arccos(angle)

    # Multiply by earth's radius to obtain distance in km
    return arc * EARTH_RADIUS

def compute(df, HAPPY_PICKUP_WALKING_DISTANCE, HAPPY_WALKING_DISTANCE, MAX_WAITING_TIME):
	print(HAPPY_PICKUP_WALKING_DISTANCE)
	print(HAPPY_WALKING_DISTANCE)
	print(MAX_WAITING_TIME)

	group_10m = df.groupby(pd.Grouper(freq=str(MAX_WAITING_TIME)+'Min'))

	collapsedJobs = []
	sharedJobs = []

	for key, item in group_10m:
		try:
			# cluster here!

			group = group_10m.get_group(key)

			# empty groups cannot be shared...
			if group.shape[0] == 1:
				continue

			# print(group.shape)
		
			pickupCoords = group.as_matrix(columns=['pickup_latitude', 'pickup_longitude'])
			pickupDistances = distance_on_sphere_numpy(pickupCoords)

			dropoffCoords = group.as_matrix(columns=['dropoff_latitude', 'dropoff_longitude'])
			dropoffDistances = distance_on_sphere_numpy(dropoffCoords)

			# for each row (trip), find the other closest trips. If there is any then determine if we can share
			# we can share if the pickup distance difference is also small
			x = 0
			for i in dropoffDistances:
				# print(i)

				y = 0
				
				candidates = []
				for j in i:
					if x == y or len(candidates) == 4:
						y = y + 1
						continue

					if j < HAPPY_WALKING_DISTANCE:
						if pickupDistances[x][y] < HAPPY_PICKUP_WALKING_DISTANCE:

							candidates.append(y)
							collapsedJobs.append(group.iloc[[y]])
							dropoffDistances[y] = np.arange(1000, 1000+dropoffDistances.shape[1], dtype=float)
					y = y + 1

				if len(candidates) > 0: 
					if len(candidates) >= 3:
						print("no way!")

					dropoffDistances[x] = np.arange(1000, 1000+dropoffDistances.shape[1], dtype=float)
					collapsedJobs.append(group.iloc[[x]])
					sharedJobs.append(group.iloc[[x]])

				x = x + 1
		except Exception:
			print(traceback.format_exc())
			# break
			# print(group_10m.get_group(key)["dropoff_latitude"])
			#
			# break

	print(len(collapsedJobs))
	print(len(sharedJobs))

	collapsedDropoffArray = []
	collapsedPickupArray = []
	sharedDropoffArray = []
	sharedPickupArray = []

	for collapsedJob in collapsedJobs:

		collapsedJobDropoffDict = {}
		collapsedJobDropoffDict["type"] = "point"
		collapsedJobDropoffDict["longitude"] = collapsedJob["dropoff_longitude"].values[0]
		collapsedJobDropoffDict["latitude"] = collapsedJob["dropoff_latitude"].values[0]
		collapsedDropoffArray.append(collapsedJobDropoffDict)

		collapsedJobPickupDict = {}
		collapsedJobPickupDict["type"] = "point"
		collapsedJobPickupDict["longitude"] = collapsedJob["pickup_longitude"].values[0]
		collapsedJobPickupDict["latitude"] = collapsedJob["pickup_latitude"].values[0]
		collapsedPickupArray.append(collapsedJobPickupDict)

	for sharedJob in sharedJobs:

		sharedJobPickupDict = {}
		sharedJobPickupDict["type"] = "point"
		sharedJobPickupDict["longitude"] = sharedJob["pickup_longitude"].values[0]
		sharedJobPickupDict["latitude"] = sharedJob["pickup_latitude"].values[0]
		sharedPickupArray.append(sharedJobPickupDict)

		sharedJobDropoffDict = {}
		sharedJobDropoffDict["type"] = "point"
		sharedJobDropoffDict["longitude"] = sharedJob["dropoff_longitude"].values[0]
		sharedJobDropoffDict["latitude"] = sharedJob["dropoff_latitude"].values[0]
		sharedDropoffArray.append(sharedJobDropoffDict)


	dataDict = {
		'collapsedDropoffArray' : collapsedDropoffArray,
		'collapsedPickupArray' : collapsedPickupArray,
		'sharedDropoffArray' : sharedDropoffArray,
		'sharedPickupArray' : sharedPickupArray,
		'totalRides' : df.shape[0],
		'collapsedRides' : len(collapsedJobs),
		'sharedRides' : len(sharedJobs),
		'algorithm' : "naiveN"	
	}

	data = json.dumps(dataDict)
		
	return data