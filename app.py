import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

"""Database Setup"""

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

"""FLASK SETUP"""
app = Flask(__name__)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        #start_date (string): A date string in the format %Y-%m-%d
        #end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX"""
    
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
"""FLASK ROUTES"""

@app.route("/")
def home():
    """List all routes that are available"""
    return(
        f"Welcome to Rebecca's SQLAlchemy Hmwk Assignment!<br/>"
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api.v1.0/<start>/<end> <br/>"
    ) 

@app.route("/api/v1.0/precipitation")
def prcp():

    final_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_str = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_str, "%Y-%m-%d")

    previous_date = max_date - dt.timedelta(365)

    prcp_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= previous_date).all()

    results = {}
    for result in prcp_data:
        results[result[0]] = result[1]


    return jsonify(results)


@app.route("/api/v1.0/stations")
def stations():


    results = session.query(Station.station).all()

    station_names = list(np.ravel(results))

    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():

    final_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_str = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_str, "%Y-%m-%d")

    previous_date = max_date - dt.timedelta(365)

    tobs_results = session.query(func.max(Measurement.station), func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all().\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()

    obsv_list = []
    for result in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = tobs_results.date
        tobs_dict["station"] = tobs_results.station
        tobs_dict["tobs"] = tobs_results.tobs
        obvs_list.append(tobs_dict)

    return jsonify(obsv_list)


@app.route("/api/v1.0/<start>")
def start():

    final_date = session.query(func.max(strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date[0][0]

    temperatures = calc_temps(start, max_date)

    temp_list = []
    temp_dict = {'start_date': start, 'end_date': max_date}
    temp_list.append(temp_dict)
    temp_list.append({'Observation': 'TMIN', 'Temperature': temperatures[0][0]})
    temp_list.append({'Observation': 'TAVG', 'Temperature': temperatures[0][1]})
    temp_list.append({'Observation': 'TMAX', 'Temperature': temperatures[0][2]})

    return jsonify(temp_list)
#@app.route("/api.v1.0/<start>/<end>")

if __name__ == "__main__":
    app.run(debug=True)