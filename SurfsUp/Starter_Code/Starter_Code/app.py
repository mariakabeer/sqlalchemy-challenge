# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import re

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#1. /

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaiian Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )

#2. /api/v1.0/precipitation

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precipitation_dict = {date: precipitation for date, precipitation in precipitation_data}

    session.close()

    print(f"Results for Precipitation - {precipitation_dict}")

    return jsonify(precipitation_dict)

#3. /api/v1.0/stations

def stations():
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

#4. /api/v1.0/tobs

def tobs():
    session = Session(engine)

    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()

    session.close()

    tobs_list = [{date: tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>

def start_date(start):
    session = Session(engine)

    results2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    temp_stats = list(np.ravel(results2))

    return jsonify(temp_stats)

def start_end_date(start, end):
    session = Session(engine)

    results3 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_stats2 = list(np.ravel(results3))

    return jsonify(temp_stats2)

if __name__ == "__main__":
    app.run(debug=True)