# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
from datetime import datetime as dt  # Import datetime for date conversion


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")  # Update the path to your database file
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation API
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2017-01-01').all()  # Adjust date as per your data
    session.close()

    # Convert query results to dictionary and convert date to proper datetime format
    precipitation_data = {dt.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d'): prcp for date, prcp in results}

    return jsonify(precipitation_data)

#Stations API
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations = [station[0] for station in results]
    return jsonify(stations)

# TOBS API
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query temperature observations for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').all()  # Adjust station ID as per your data
    session.close()

    # Convert query results to dictionary and convert date to proper datetime format
    temperature_data = {dt.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d'): tobs for date, tobs in results}

    return jsonify(temperature_data)

# Start date API
@app.route("/api/v1.0/<start>")
def start_temp_stats(start):
    # Convert start date string to a datetime object
    start_date = dt.strptime(start, "%Y-%m-%d")
    
    # Query to calculate min, avg, and max temperatures for dates >= start date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).all()

    # Convert the results into a dictionary for easy JSON conversion
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_stats)

# Start/End date API
@app.route("/api/v1.0/<start>/<end>")
def start_end_temp_stats(start, end):
    # Convert start and end date strings to datetime objects
    start_date = dt.strptime(start, "%Y-%m-%d")
    end_date = dt.strptime(end, "%Y-%m-%d")

    # Query to calculate min, avg, and max temperatures for the date range
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the results into a dictionary for easy JSON conversion
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return JSON representation of the results
    return jsonify(temp_stats)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)