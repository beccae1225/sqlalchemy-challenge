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

    session = Session(engine)

    final_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_str = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_str, "%Y-%m-%d")

    previous_date = max_date - dt.timedelta(365)

    prcp_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= previous_date).all()

    results = {}
    for result in prcp_data:
        results[result[0]] = result[1]

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    station_names = list(np.ravel(results))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    final_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_str = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_str, "%Y-%m-%d")

    previous_date = max_date - dt.timedelta(365)

    tobs_results = session.query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= previous_date).all().\
        filter(Measurement.station == 'USC005119281').all()

    session.close()

    obvs_list = []
    for result in tobs_results:
        tobs_dictionary = {}
        tobs_dictionary["date"] = result.date
        tobs_dictionary["station"] = result.station
        tobs_dictionary["tobs"] = result.tobs
        obvs_list.append(tobs_dictionary)

    return jsonify(obvs_list)

@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    final_date = session.query(func.max(strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date[0][0]

    def calc_temps(start_date, end_date):
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    temps = calc_temps(start, max_date)

    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})        
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})        
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)        

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    temperatures = calc_temps(start, end)

    temp_return_list = []
    date_dictionary = {'start_date': start, 'end_date': end}
    temp_return_list.append(date_dictionary)
    temp_return_list.append({'Observation': 'TMIN', 'Temperature': temperatures[0][0]})        
    temp_return_list.append({'Observation': 'TAVG', 'Temperature': temperatures[0][1]})        
    temp_return_list.append({'Observation': 'TMAX', 'Temperature': temperatures[0][2]})

    return jsonify(temp_return_list)

if __name__ == "__main__":
    app.run(debug=True)