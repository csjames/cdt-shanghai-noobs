import pandas as pd
import numpy as np
import json
import traceback
import osrm


osrm.RequestConfig.host = "http://localhost:5001"
print(osrm.RequestConfig)

MAX_WAITING_TIME = 10

LATENESS_ADJUSTER = 300
EARLY_PICKUP_ADJUSTER = 300

kms_per_radian = 6371.0088
epsilon = 1.5 / kms_per_radian

def compute(df):

	group_10m = df.groupby(pd.Grouper(freq=str(MAX_WAITING_TIME)+'Min'))

	collapsedJobs = []
	sharedJobs = []

	doable = 0
	total = 0

	dfg = 0

	rides = []

	for key, item in group_10m:
		try:
			# cluster here!

			group = group_10m.get_group(key)

			# empty groups cannot be shared...
			if group.shape[0] == 1:
				continue

			# list_coord = [[21.0566163803209, 42.004088575972],
			# [21.3856064050746, 42.0094518118189],
			# [20.9574645547597, 41.5286973392856],
			# [21.1477394809847, 41.0691482795275],
			# [21.5506463080973, 41.3532256406286]]

			# list_id = ['name1', 'name2', 'name3', 'name4', 'name5']

			# time_matrix, snapped_coords = osrm.table(list_coord,
			#                                   				  ids_origin=list_id,
			#                                   				  output='dataframe')

			dropoffCoords = group.as_matrix(columns=['dropoff_longitude', 'dropoff_latitude'])
			# print(len(dropoffCoords)) 

			time_matrix = osrm.table(dropoffCoords,
			                                  				  ids_origin=np.arange(len(dropoffCoords)),
			                                  				  ids_dest=np.arange(len(dropoffCoords)),
			                                  				  output='dataframe',
			                                  				  send_as_polyline=False)

			# print(time_matrix)
			time_matrix_delay = np.add(time_matrix, + LATENESS_ADJUSTER)

			print("OSRM Table Returned")
		
			x = 0

			dfg = 0

			marked = []
	
			for i in time_matrix:
				# tollerable means different between pickup and dropoff is minimal

				y = 0
			
				for j in i:
					if x==y or time_matrix_delay[x][y] == 0 or time_matrix_delay[x][y] == LATENESS_ADJUSTER:
						y = y + 1
						# if x != y:
						# 	print(str(x) + " " + str(y))
						continue

					first = group.iloc[[x]]
					second = group.iloc[[y]]

					# is first pickup before second
					# consider change of duration for second ride aswell!
					if pd.Timedelta(second["pickup_datetime"].values[0] - first["pickup_datetime"].values[0]).seconds >= 0 and pd.Timedelta(second.index.values[0] - first.index.values[0]).seconds < time_matrix_delay[x][y]:
						# is pickup time realistic?
						result = osrm.simple_route(
	                      [first["pickup_longitude"].values[0],first["pickup_latitude"].values[0]],
	                       [second["pickup_longitude"].values[0],second["pickup_latitude"].values[0]],
	                      output='route', geometry='wkt',send_as_polyline=True)

						extended_trip_time = result[0]["duration"]*2

						if pd.Timedelta(first["pickup_datetime"].values[0] - second["pickup_datetime"].values[0]).seconds <= extended_trip_time + EARLY_PICKUP_ADJUSTER:
						# if True:
							# print("Tollerable")
							# how long does journey take?
							# pickup first, pickup_second, dropoff_first, dropoff_second,  
							first_result = osrm.simple_route(
		                      [first["pickup_longitude"].values[0],first["pickup_latitude"].values[0]],
		                       [first["dropoff_longitude"].values[0],first["dropoff_latitude"].values[0]],
		                      [[second["pickup_longitude"].values[0],second["pickup_latitude"].values[0]]],
		                      output='route', geometry='wkt',send_as_polyline=True)

							first_trip_time = first["trip_time_in_secs"].values[0]
							extended_first_trip_time = first_result[0]["duration"]			

							if extended_first_trip_time < first_trip_time + LATENESS_ADJUSTER:
								# print("no friggin way")

								second_result = osrm.simple_route(
			                         [second["pickup_longitude"].values[0],second["pickup_latitude"].values[0]],
			                       [second["dropoff_longitude"].values[0],second["dropoff_latitude"].values[0]],
			                      [[first["dropoff_longitude"].values[0],first["dropoff_latitude"].values[0]]],
			                      output='route', geometry='wkt', send_as_polyline=True)

								second_trip_time = second["trip_time_in_secs"].values[0]
								extended_second_trip_time = second_result[0]["duration"]

								if extended_second_trip_time < second_trip_time + LATENESS_ADJUSTER  :
									# print("no friggin way")
									
									dfg+=1

									result = osrm.simple_route(
				                         [first["pickup_longitude"].values[0],first["pickup_latitude"].values[0]],
				                       [second["dropoff_longitude"].values[0],second["dropoff_latitude"].values[0]],
				                      [[second["pickup_longitude"].values[0],second["pickup_latitude"].values[0]],
				                      [first["dropoff_longitude"].values[0],first["dropoff_latitude"].values[0]]],
			                      output='route', geometry='geojson', send_as_polyline=True)


									collapsedJobs.append(group.iloc[[x]])
									collapsedJobs.append(group.iloc[[y]])

									ride = {}
									ride["pickup_first"] = {}
									ride["pickup_first"]["type"] = "point"
									ride["pickup_first"]["latitude"] = first["pickup_latitude"].values[0]
									ride["pickup_first"]["longitude"] = first["pickup_longitude"].values[0]

									ride["dropoff_first"] = {}
									ride["dropoff_first"]["type"] = "point"
									ride["dropoff_first"]["latitude"] = first["dropoff_latitude"].values[0]
									ride["dropoff_first"]["longitude"] = first["dropoff_longitude"].values[0]

									ride["pickup_second"] = {}
									ride["pickup_second"]["type"] = "point"
									ride["pickup_second"]["latitude"] = second["pickup_latitude"].values[0]
									ride["pickup_second"]["longitude"] = second["pickup_longitude"].values[0]

									ride["dropoff_second"] = {}
									ride["dropoff_second"]["type"] = "point"
									ride["dropoff_second"]["latitude"] = second["dropoff_latitude"].values[0]
									ride["dropoff_second"]["longitude"] = second["dropoff_longitude"].values[0]

									# print(second_result)

									ride["geometry"] = result[0]["geometry"]

									rides.append(ride)

									marked.append(x)
									marked.append(y)

									g = 0
									for k in i:
										print(x)
										time_matrix_delay[x][g] = 0
										time_matrix_delay[y][g] = 0
										time_matrix_delay[g][x] = 0
										time_matrix_delay[g][y] = 0
										g+=1
										# print(g)


								else: 
									l = 0
							else: 
								l = 1
						else:
							l = 3
					else:
						l = 2
					y = y + 1
				x = x + 1

			total+=group.shape[0]
			doable+=dfg

			print("Total")
			print(total)
			print("Doable")
			print(doable)

			if (doable > 20):
				break

			
		except Exception:
			print(traceback.format_exc())
			# continue
			# break
			# break
			# print(group_10m.get_group(key)["dropoff_latitude"])
			#
			# break

	collapsedDropoffArray = []
	collapsedPickupArray = []

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

	dataDict = {
		'collapsedDropoffArray' : collapsedDropoffArray,
		'collapsedPickupArray' : collapsedPickupArray,
		'rides' : rides,
		'totalRides' : total,
		'collapsedRides' : doable*2,
		'sharedRides' : doable,
		'algorithm' : "Minimal Delay"	
	}

	# print(json.dumps(dataDict))
	data = json.dumps(dataDict)
		
	return data

	# print(len(collapsedJobs))
	# print(len(sharedJobs))

	# collapsedDropoffArray = []
	# collapsedPickupArray = []
	# sharedDropoffArray = []
	# sharedPickupArray = []

	# for collapsedJob in collapsedJobs:

	# 	collapsedJobDropoffDict = {}
	# 	collapsedJobDropoffDict["type"] = "point"
	# 	collapsedJobDropoffDict["longitude"] = collapsedJob["dropoff_longitude"].values[0]
	# 	collapsedJobDropoffDict["latitude"] = collapsedJob["dropoff_latitude"].values[0]
	# 	collapsedDropoffArray.append(collapsedJobDropoffDict)

	# 	collapsedJobPickupDict = {}
	# 	collapsedJobPickupDict["type"] = "point"
	# 	collapsedJobPickupDict["longitude"] = collapsedJob["pickup_longitude"].values[0]
	# 	collapsedJobPickupDict["latitude"] = collapsedJob["pickup_latitude"].values[0]
	# 	collapsedPickupArray.append(collapsedJobPickupDict)

	# for sharedJob in sharedJobs:

	# 	sharedJobPickupDict = {}
	# 	sharedJobPickupDict["type"] = "point"
	# 	sharedJobPickupDict["longitude"] = sharedJob["pickup_longitude"].values[0]
	# 	sharedJobPickupDict["latitude"] = sharedJob["pickup_latitude"].values[0]
	# 	sharedPickupArray.append(sharedJobPickupDict)

	# 	sharedJobDropoffDict = {}
	# 	sharedJobDropoffDict["type"] = "point"
	# 	sharedJobDropoffDict["longitude"] = sharedJob["dropoff_longitude"].values[0]
	# 	sharedJobDropoffDict["latitude"] = sharedJob["dropoff_latitude"].values[0]
	# 	sharedDropoffArray.append(sharedJobDropoffDict)


	# dataDict = {
	# 	'collapsedDropoffArray' : collapsedDropoffArray,
	# 	'collapsedPickupArray' : collapsedPickupArray,
	# 	'sharedDropoffArray' : sharedDropoffArray,
	# 	'sharedPickupArray' : sharedPickupArray,
	# 	'totalRides' : df.shape[0],
	# 	'collapsedRides' : len(collapsedJobs),
	# 	'sharedRides' : len(sharedJobs),
	# 	'algorithm' : "naiveN"	
	# }

	# data = json.dumps(dataDict)
		
	# return data
	return