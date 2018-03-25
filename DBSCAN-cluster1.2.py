from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
import json
import datetime as dt
from dateutil.relativedelta import *
#import  DNN1
# two parameters not used , and i think we need to find the relation between epsilon and HAPPY_PICKUP_WALKING_DISTANCE, HAPPY_WALKING_DISTANCE
def compute(df, HAPPY_PICKUP_WALKING_DISTANCE, HAPPY_WALKING_DISTANCE, MAX_WAITING_TIME):
    # espslion here should depend on HAPPY_PICKUP_WALKING_DISTANCE, HAPPY_WALKING_DISTANCE,
    epsilon = (HAPPY_PICKUP_WALKING_DISTANCE+HAPPY_WALKING_DISTANCE) / 6371.0088  # kilometers per radian
    a = 2
    # this one for me to divide data by time
    initial = dt.datetime.strptime('2013-11-25 00:00:00', '%Y-%m-%d %H:%M:%S')

    collapsedDropoffArray = []
    collapsedPickupArray = []
    sharedDropoffArray = []
    sharedPickupArray = []
    used = []
    for i in range(1,int(24*60/MAX_WAITING_TIME)):
        # chose 10min data
        try:
            df0 = df.loc[(df['dropoff_datetime']>initial)&(df['dropoff_datetime']<initial+relativedelta(minutes=+MAX_WAITING_TIME))]
            initial = initial + relativedelta(minutes=+MAX_WAITING_TIME)

            #print('batch=', i)

            df0 = df0.reset_index(drop=True)

        #dfp = pd.DataFrame(df0,columns=['passenger_count','pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude'])
                          # index = range(df0.iloc[:,0].size))
            dfp = df0.loc[:,['passenger_count','pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude']]
                    #  index = np.arange(len(df0.index)))

            coords1 = dfp.as_matrix(columns=['pickup_longitude','pickup_latitude'])
            coords2 = dfp.as_matrix(columns=['dropoff_longitude','dropoff_latitude'])
        # the dbscan things

            db1 = DBSCAN(eps=epsilon, min_samples=a, algorithm='ball_tree', metric='haversine').fit(np.radians(coords1))
            lables1 = db1.labels_
            n_clusters_1 = len(np.unique(lables1)) - (1 if -1 in lables1 else 0)
            print("n_clusters_1=",n_clusters_1)

            db2 = DBSCAN(eps=epsilon, min_samples=a, algorithm='ball_tree', metric='haversine').fit(np.radians(coords2))
            lables2 = db2.labels_
            n_clusters_2 = len(np.unique(lables2)) - (1 if -1 in lables2 else 0)
            print("n_clusters_2=", n_clusters_2)
        #shared = pd.DataFrame()
        #df1 = df
# double for loop to find those both labels_ are equal
            print(lables1)

            for j in range(len(dfp.index)-1):
# exclude labels= -1 which is noise
                used0 = []
                if (j not in used0) & (db1.labels_[j]!=-1) & (db2.labels_[j]!=-1):
                    for k in range(len(dfp.index)-1):
                        if (k not in used0) and (k!=j) & (db1.labels_[k]!=-1) & (db2.labels_[k]!=-1):
                    # the pass_count shall be < 5 in all
                            used_label = []
                            if (db1.labels_[j] == db1.labels_[k])&(db2.labels_[j] == db2.labels_[k])&((dfp.iloc[j,0]+dfp.iloc[k,0])<5):
                                used.append(j)
                                used.append(k)
                                used0.append(j)
                                used0.append(k)
                                #used_label.append(j,k)
                            # export the parameter
                                collapsedJobDropoffDict = {}
                                collapsedJobDropoffDict['type'] = 'point'
                                collapsedJobDropoffDict['longitude'] = dfp.loc[j, 'dropoff_longitude']
                                collapsedJobDropoffDict['latitude'] = dfp.loc[j, 'dropoff_latitude']
                                collapsedDropoffArray.append(collapsedJobDropoffDict)
                                #print(collapsedJobDropoffDict)
                                collapsedJobPickupDict = {}
                                collapsedJobPickupDict['type'] = 'point'
                                collapsedJobPickupDict['longitude'] = dfp.loc[j, "pickup_longitude"]
                                collapsedJobPickupDict['latitude'] = dfp.loc[j, 'pickup_latitude']
                                collapsedPickupArray.append(collapsedJobPickupDict)
                                #print(collapsedJobPickupDict)
                                sharedJobPickupDict = {}
                                sharedJobPickupDict["type"] = "point"
                                sharedJobPickupDict["longitude"] = dfp.loc[k, "pickup_longitude"]
                                sharedJobPickupDict["latitude"] = dfp.loc[k, "pickup_latitude"]
                                sharedPickupArray.append(sharedJobPickupDict)
                                #print(sharedJobPickupDict)
                                sharedJobDropoffDict = {}
                                sharedJobDropoffDict["type"] = "point"
                                sharedJobDropoffDict["longitude"] = dfp.loc[k, 'dropoff_longitude']
                                sharedJobDropoffDict["latitude"] = dfp.loc[k, 'dropoff_latitude']
                                sharedDropoffArray.append(sharedJobDropoffDict)
                                break
                                #print(sharedJobDropoffDict)
                            # dnn things, not done yet
                            #df_dnn = dfp.loc[used_label,'pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude']
                            #df_dnn['index1'] = pd.Series(range(len(df_dnn.index)),index=range(len(df_dnn.index)))

                            #print (df_dnn)

                            #df_dnn0=df_dnn.value

                            #distant = DNN1.dnn_learning(df_dnn0)


        except Exception:
            print('somethingwrong')
            pass
    dataDict = {
        'collapsedDropoffArray': collapsedDropoffArray,
        'collapsedPickupArray': collapsedPickupArray,
        'sharedDropoffArray': sharedDropoffArray,
        'sharedPickupArray': sharedPickupArray,
        'totalRides': df.shape[0],
        'collapsedRides': len(used) / 2,
        'sharedRides': len(used) / 2,
        'algorithm': 'DBSCAN'}
    print(len(collapsedDropoffArray))
    data = json.dumps(dataDict)
    return data

'''#test
def parse_dates(x):
    return dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
inputfile = r'C:\Users\evanxephon\Desktop\NYCFareData\2013-11-25.csv'

df00 = pd.read_csv(inputfile,names=['medallion','hack_license','vendor_id','rate_code','store_and_fwd_flag','pickup_datetime','dropoff_datetime','passenger_count',
                                    'trip_time_in_secs','trip_distance','pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude'],
                 parse_dates=["pickup_datetime", "dropoff_datetime"],date_parser=parse_dates)

df00.drop(["medallion", "hack_license"], axis=1, inplace=True)
# clean data of NaN ,but it seems not work
df00.dropna(axis=0)
df00 = df00.loc[df00['passenger_count']<4]
#for t in range(10,1000,10):
print(compute(df00,0.05,0.05,10))'''
