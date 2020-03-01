# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy import and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

import datetime as dt
# source: https://dateutil.readthedocs.io/en/stable/
from dateutil.relativedelta import relativedelta

# Custom functions file this project
from my_functions import get_date_str, declutter_plot

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

from flask import Flask, jsonify

# Set-up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)
# stop flask.jsonify() from sorting data by keys
app.config['JSON_SORT_KEYS'] = False

# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    """List all available api routes."""
    print('LOG: This is the HOMEPAGE.')
    return (
        f"Welcome to ClimateApp<br/>"
        f"<br/>"
        f"Available Routes:-<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print('LOG: This is PRECIPITATION page.')
    session = Session(engine)

    # Find most recent data entry in the data set
    results = session.query(Measurement.date,
                            Measurement.prcp).all()
    session.close()

    # Sanity check
    print(f'LOG: Length of query results: {len(results)}')

    # Convert list of tuples into dict
    # precipitation_dict = dict(results)

    all_prcp_dict = []

    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['precipitation'] = prcp
        all_prcp_dict.append(prcp_dict)

    return(
        jsonify(all_prcp_dict)
        # precipitation_dict
    )


# @app.route("/api/v1.0/stations")
# def stations():
#     print('LOG: This is the STATIONS page')
#     session = Session(engine)

#     # Find most recent data entry in the data set
#     results = session.query(Station.id,
#                             Station.station,
#                             Station.name,
#                             Station.latitude,
#                             Station.longitude,
#                             Station.elevation
#                             ).all()
#     session.close()

#     all_stations_dict = []

#     for station_id, station, name, lat, lng, elev in results:
#         station_dict = {}
#         station_dict['id'] = station_id
#         station_dict['station'] = station
#         station_dict['name'] = name
#         station_dict['latitude'] = round(lat, 2)
#         station_dict['longitude'] = round(lng, 2)
#         station_dict['elevation'] = round(elev, 2)
#         all_stations_dict.append(station_dict)

#     return(
#         jsonify(all_stations_dict)
#         # precipitation_dict
#     )

# Assuming we were required to perform joins on the two classes to
# obtain all th estations from the database
@app.route("/api/v1.0/stations")
def stations_joined():
    print('LOG: This is the STATIONS page')
    session = Session(engine)

    sel = [Measurement.id, Measurement.station, Measurement.date,
           Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    # Find most recent data entry in the data set
    results = session.query(
        *sel).filter(Measurement.station == Station.station).all()

    session.close()

    # print on terminal for debugging
    for record in results:
        (m_id, m_station, m_date, s_id, s_station,
         s_name, s_lat, s_lng, s_elev) = record
        print(
            f'LOG: {m_id}, {m_station}, {m_date}, {s_id}, {s_name}, {round(s_lat, 2)}, {round(s_lng, 2)}, {round(s_elev, 2)}')
        break

    all_stations_dict = []

    for record in results:
        (m_id, m_station, m_date, s_id, s_station,
         s_name, s_lat, s_lng, s_elev) = record
        station_dict = {}
        station_dict['measurement_id'] = m_id
        station_dict['station_id'] = s_id
        station_dict['station'] = m_station
        station_dict['name'] = s_name
        station_dict['latitude'] = round(s_lat, 2)
        station_dict['longitude'] = round(s_lng, 2)
        station_dict['elevation'] = s_elev
        station_dict['meaurement_date'] = m_date
        all_stations_dict.append(station_dict)

    return jsonify(all_stations_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    print('LOG: This is the TOBS (temperature_observations) page')
    session = Session(engine)

    # Find most recent data entry in the data set
    result = session.query(Measurement.id,
                           Measurement.date,
                           Measurement.tobs).\
        order_by(Measurement.id.desc()).\
        first()
    # Grab the most recent entry in the database and find 12 month prior date programatically
    most_recent_entry_date = result[1]
    most_recent_entry_date = dt.datetime.strptime(
        most_recent_entry_date, '%Y-%m-%d')
    print(
        f'LOG: Date of last entry in the database: {most_recent_entry_date.strftime("%b")} {most_recent_entry_date.day}, {most_recent_entry_date.year}')

    twelve_months_prior_date = most_recent_entry_date - \
        relativedelta(months=12)
    print(
        f'LOG: Twelve months prior date: {twelve_months_prior_date.strftime("%b")} {twelve_months_prior_date.day}, {twelve_months_prior_date.year}')

    # Retrieve last 12 months of precipitation data from the most recent entry in the database
    results = session.query(Measurement.date,
                            Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= get_date_str(twelve_months_prior_date)).\
        all()
    # Sanity check
    print(f'LOG: length of query results:  {len(results)}')

    session.close()

    all_tobs_dict = []

    for date, tob in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temperature'] = tob
        all_tobs_dict.append(tobs_dict)

    return jsonify(all_tobs_dict)


@app.route("/api/v1.0/<start_date>")
def temperature_stats(start_date):
    print('LOG: This is the TOBS START_DATE page')

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    tobs_stats_dict = []

    for min_tobs, avg_tobs, max_tobs in results:
        tobs_dict = {}
        tobs_dict['start_date'] = start_date
        tobs_dict['minimum_temperature'] = round(min_tobs, 2)
        tobs_dict['average_temperature'] = round(avg_tobs, 2)
        tobs_dict['maximum_temperature'] = round(max_tobs, 2)
        tobs_stats_dict.append(tobs_dict)

    return (
        jsonify(tobs_stats_dict)
    )


@app.route("/api/v1.0/<start_date>/<end_date>")
def temperature_stats_start_end(start_date, end_date):
    print('LOG: This is the TOBS START_DATE/END_DATE page')

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(and_(Measurement.date >= start_date,
                    Measurement.date <= end_date)).all()

    session.close()

    tobs_stats_dict = []

    for min_tobs, avg_tobs, max_tobs in results:
        tobs_dict = {}
        tobs_dict['start_date'] = start_date
        tobs_dict['end_date'] = end_date
        tobs_dict['minimum_temperature'] = round(min_tobs, 2)
        tobs_dict['average_temperature'] = round(avg_tobs, 2)
        tobs_dict['maximum_temperature'] = round(max_tobs, 2)
        tobs_stats_dict.append(tobs_dict)

    return (
        jsonify(tobs_stats_dict)
    )


if __name__ == "__main__":
    app.run(debug=True)
