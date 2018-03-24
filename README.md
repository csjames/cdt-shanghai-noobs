# cdt-shanghai-noobs
Visualisation of Ride Sharing

## Simple Ride Sharing 

Congestion in inner cities is an increasingly large problem, not helped by the precense of taxis, due to their poor passenger to vehicle size ratio. To reduce this, whilst still enabling people to take taxis, journeys can be shared.

Ride sharing algorithms vary in complexity and may optimise for various factors such as ride cost, mileage, or walking distance. 

### Progress

Basic visualisation of rides
Naive algorthithm which looks only at similiar pickup and dropoff locations, as well as similiar dropoff time.

### Next Steps

Implement less naive algorithms to increase percentage of shared rides.


## Initial Data Reduction

### Terminal commands for quick data partitioning... Props easy with panda also

```awk -F "," data_file.csv 'if $6 ~ /2013-03-25/ { print $0 }' > 2013-03-25.csv # ~ 500k lines```

```head -n 20000 2013-03-25.csv > 2013-03-25-20k.csv```

```head -n 2000 2013-03-25.csv > 2013-03-25-2k.csv ```

```head -n 200 2013-03-25.csv > 2013-03-25-200.csv # Now we have some data we can quickly test on```


```tail -k offset_count -n 2000 2013-03-25.csv > 2013-03-25-2k.csv ```
