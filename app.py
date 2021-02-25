# import dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import numpy as np 
import datetime as dt 

# set up database connection
engine = create_engine('sqlite:///hawaii.sqlite')
# reflect database
Base = automap_base()
#reflect tables
Base.prepare(engine, reflect=True)
# var for tables
Measurement = Base.classes.measurement
Station = Base.classes.station 
# create session for API
session = Session(engine)
# use flask to set up app to view data
app = Flask(__name__)
# flask routes
#home route
@app.route('/')
def welcome():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start><br/>"
        f"/api/v1.0/start_end/<start>/<end><br/>"
    )

# precip route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # create session for API
    session = Session(engine)
    print("Server received request for 'Precipietion' page...")
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    #close session for next query
    session.close()
    #store the data for json 
    all_prcp = []
    #loop the database call for the prcip data
    for date, prcp in precip_data:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)
    return jsonify(all_prcp)

# stations route
@app.route('/api/v1.0/stations')
def stations():
    # create session for API
    session = Session(engine)
    print("Server received request for 'Stations' page...")
    #get station names
    station_data = session.query(Station.station).all()
    station_names = list(np.ravel(station_data))
    #close session for next query
    session.close()
    return jsonify(station_names)

# tobs route
@app.route('/api/v1.0/tobs')
def tobs():
    # create session for API
    session = Session(engine)
    print("Server received request for 'TOBS' page...")
    # find one year prior date 
    one_year_ago = dt.date(2017,8,18) - dt.timedelta(days=365)
    temps = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
            filter(Measurement.station=='USC00519281').\
            filter(Measurement.date>=one_year_ago).all()
    #close session for next query
    session.close()
    return jsonify(temps)  

# custom start to end route
@app.route('/api/v1.0/start_date/<start>')
def start_date(start):
    # create session for API
    session = Session(engine)
    print("Server received request for 'Start_Date' page...")
    #When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    #query Data base
    data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    #close session for next query
    session.close()
    # retrieve data
    #dict to retrun from
    t_normals = []
    # loop to retrieve data
    for min_tobs, avg_tobs, max_tobs in data:
        #dict for each iteration
        tobs_dict = {}
        tobs_dict["MIN TOBS"] = min_tobs
        tobs_dict["AVG TOBS"] = avg_tobs
        tobs_dict["MAX TOBS"] = max_tobs
        t_normals.append(tobs_dict)
    return jsonify(t_normals)

# custom date range route
@app.route('/api/v1.0/start_end/<start>/<end>')
def custom_range(start,end):
    # create session for API
    session = Session(engine)
    print("Server received request for 'Custom_Range' page...")
    data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date<=end).all()
    #close session for next query
    session.close()
    # retrieve data
    #dict to retrun from
    t_normals = []
    # loop to retrieve data
    for min_tobs, avg_tobs, max_tobs in data:
        #dict for each iteration
        tobs_dict = {}
        tobs_dict["MIN TOBS"] = min_tobs
        tobs_dict["AVG TOBS"] = avg_tobs
        tobs_dict["MAX TOBS"] = max_tobs
        t_normals.append(tobs_dict)
    return jsonify(t_normals)

#keeps flask running while open
if __name__ == "__main__":
    app.run(debug=True)