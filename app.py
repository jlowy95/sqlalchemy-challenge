import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify, request

################
# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Prepare classes
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

################
# Flask Setup
app = Flask(__name__)

# Flask Routes

# Home Page
@app.route('/')
# List all routes available
def welcome():
    return (
        f"Welcome to Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"'/' - Home<br/>"
        f"'/api/v1.0/precipitation' - Precipitation by Date<br/>"
        f"'/api/v1.0/stations' - List of Stations<br/>"
        f"'/api/v1.0/tobs' - Temperature by Date<br/>"
        f"'/api/v1.0/<start>' - Temperature Stats after a specified Date<br/>"
        f"'/api/v1.0/<start>/<end>' - Temperatures Stats for a specified Period"
    )

# Precipitation by Date
@app.route('/api/v1.0/precipitation')
def prcp():
    session = Session(engine)

    prcp = {}
    for row in session.query(Measurement.date, Measurement.prcp):
        prcp[row[0]] = row[1]
    
    session.close()

    return jsonify(prcp)

# List of Stations
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    stations = {}
    for row in session.query(Station.station, Station.name):
        stations[row[0]] = row[1]

    session.close()

    return jsonify(stations)

# Temperature by Date 
# for the last year of data
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    # Find date one year from last date in dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0],'%Y-%m-%d')
    last_date -= dt.timedelta(days=365)
    one_year_ago = dt.datetime.strftime(last_date,'%Y-%m-%d')

    temps = {}
    for row in session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago):
        temps[row[0]] = row[1]

    session.close()

    return jsonify(temps)

# Temperature Stats
# from a specified start date
@app.route('/api/v1.0/<start>')
def temp_start(start):
    session = Session(engine)

    stats = {}
    temp_query = session.query(func.max(Measurement.tobs), func.avg(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start)
    
    stats['Max Temp'] = temp_query[0][0]
    stats['Avg. Temp'] = temp_query[0][1]
    stats['Min Temp'] = temp_query[0][2]

    session.close()

    return stats


# Temperature Stats
# for a specified period
@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start,end):
    session = Session(engine)

    stats = {}
    temp_query = session.query(func.max(Measurement.tobs), func.avg(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end)
    
    stats['Max Temp'] = temp_query[0][0]
    stats['Avg. Temp'] = temp_query[0][1]
    stats['Min Temp'] = temp_query[0][2]

    session.close()

    return stats

# Run app
if __name__ == '__main__':
    app.run(debug=True)
