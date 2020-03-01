import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
   # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    prcp_list = []
    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp
       # prcp_dict["prcp"] = prcp
    prcp_list.append(prcp_dict)
  # Return the JSON representation of your dictionary.
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    #query for the dates and temperature observations from a year from the last data point.
    session = Session(engine)
    #latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    oneyearbefore = dt.datetime(2016,8,23)

    precip_results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date > oneyearbefore).all()

    session.close()
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    all_prcp = list(np.ravel(precip_results))
    return jsonify(all_prcp)


@app.route("/api/v1.0/<start>")
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
def startdate(start):
    session = Session(engine)
    start_only = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    return jsonify(start_only)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(start_end)


if __name__ == "__main__":
    app.run(debug=True)