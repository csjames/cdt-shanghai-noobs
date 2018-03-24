import pandas as pd
import numpy as np
import datetime as dt
from sklearn.cluster import DBSCAN
epsilon = 0.1 / 6371.0088 # kilometers per radian
a = 4
min = 10
def parse_dates(x):
    return dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

print ("Reading CSV...")

df = pd.read_csv('2013-11-25-1.csv',
 names=["medallion", "hack_license", "vendor_id", "rate_code", "store_and_fwd_flag", "pickup_datetime", "dropoff_datetime", "passenger_count", "trip_time_in_secs", "trip_distance", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude"],
 parse_dates=["pickup_datetime", "dropoff_datetime"],
 index_col="dropoff_datetime",
 date_parser=parse_dates)

df.drop(["medallion", "hack_license"], axis=1, inplace=True)

#print(df.columns.values.tolist())
#print(df.dtypes)
#print(df.count)

group_10m = df.groupby(pd.Grouper(freq='10Min'))
start=0
#print(group_10m.groups)
for key,item in group_10m:
    start=start+1
    try:   
        ab = pd.DataFrame(item,columns=['pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude','passenger_count'])
        coords1 = ab.as_matrix(columns=['pickup_longitude','pickup_latitude'])
        coords2 = ab.as_matrix(columns=['dropoff_longitude','dropoff_latitude'])
        db1 = DBSCAN(eps=epsilon, min_samples=a, algorithm='ball_tree', metric='haversine').fit(np.radians(coords1))
        lables1 = db1.labels_
        n_clusters_1 = len(np.unique(lables1)) - (1 if -1 in lables1 else 0)
        print("n_clusters_1=",n_clusters_1)
        db2 = DBSCAN(eps=epsilon, min_samples=a, algorithm='ball_tree', metric='haversine').fit(np.radians(coords2))
        lables2 = db2.labels_
        n_clusters_2 = len(np.unique(lables2)) - (1 if -1 in lables2 else 0)
        print("n_clusters_2=", n_clusters_2)
        shared = pd.DataFrame()
        df1 = ab
        used = []
        print(lables1)
        for j in range((ab.iloc[:,0].size)-1):
            if (j not in used) and (db1.labels_[j]!=-1) and (db2.labels_[j]!=-1):
                for k in range((ab.iloc[:,0].size)-1):
                    if (k not in used) and (k!=j)and (db1.labels_[k]!=-1) and (db2.labels_[k]!=-1):
                        if (db1.labels_[j] == db1.labels_[k])&(db2.labels_[j] == db2.labels_[k]):
                                df1 = df1.drop([j,k])
                                used.append(j)
                                used.append(k)
                                shared = shared.append(ab.iloc[[j,k]])
        print('process'+str(start))
        shared.to_csv('/Users/fychaobajinnvgong/Desktop/321/'+str(start)+'shared.csv')
        df1.to_csv('/Users/fychaobajinnvgong/Desktop/321/'+str(start)+'remain.csv')       
    except Exception:
        print('fuck')
        pass