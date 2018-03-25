# cdt-shanghai-noobs

Visualisation of Ride Sharing Algorithms

## Simple Ride Sharing 

Congestion in inner cities is an increasingly large problem, not helped by the precense of taxis, due to their poor passenger to vehicle size ratio. To reduce this, whilst still enabling people to take taxis, journeys can be shared.

Ride sharing algorithms vary in complexity and may optimise for various factors such as ride cost, mileage, or walking distance. 

### Progress

Basic visualisation of rides
Naive algorthithm which looks only at similiar pickup and dropoff locations, as well as similiar dropoff time.
Minimal Delay: Algorithm which joins pairs of rides based on acceptable dropoff time delays.

### Running the Server and viewing Visualizations

* Install OSRM - Follow guide https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM and configure to run on port 5001 (5000 is used by server)

* Setup with a New York map export, or preferably a North America export to capture adjacent areas 

* Install anaconda https://www.anaconda.com/download

* pip3 install geopy flask

* Install osrm python bindings ```cd python-osrm && python setup.py install``` This library required modifications to function correctly as OSRM API changed recently

* Run with ```FLASK_APP=main.py flask run ```

* Navigate to http://localhost:5000/index.html

## Datasets

Inside this repository are some reduced data sets for quick algorithm testing. They all start with 2013-03-25 and do not have the data headers included.

### Terminal commands for quick data partitioning

```awk -F "," data_file.csv 'if $6 ~ /2013-03-25/ { print $0 }' > 2013-03-25.csv # ~ 500k lines```

```head -n 20000 2013-03-25.csv > 2013-03-25-20k.csv```

```head -n 2000 2013-03-25.csv > 2013-03-25-2k.csv ```

```head -n 200 2013-03-25.csv > 2013-03-25-200.csv # Now we have some data we can quickly test on```

```tail -k offset_count -n 2000 2013-03-25.csv > 2013-03-25-2k.csv ```
