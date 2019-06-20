from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import os, csv, math
import html,json
# import dateutil.parser
# from datetime import datetime, timedelta
# from pytz import timezone
# import pytz
# from timezonefinder import TimezoneFinder
# import random, redis, hashlib, pickle, numpy

myapp = Flask(__name__)

myapp.config['MYSQL_HOST'] = 'swapnilserver.mysql.database.azure.com'
myapp.config['MYSQL_USER'] = 'swapniljangam@swapnilserver'
myapp.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
myapp.config['MYSQL_DB'] = os.environ['MYSQL_DB']

mysql = MySQL(myapp)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
port = int(os.getenv("PORT", 5000))

def get_connection():
    return mysql.connection

@myapp.route("/")
def hello():
    return render_template("index.html")


@myapp.route('/random-queries', methods=['GET'])
def get_random_queries():
    conn = get_connection()
    cur = conn.cursor()
    magFrom = request.args['magFrom']
    magTo = request.args['magTo']
    sql = "SELECT net,mag FROM earthquake WHERE mag BETWEEN "+ str(magFrom) +" and "+ str(magTo)
    cur.execute(sql)
    data = cur.fetchall()
    x = [ row[0] for row in data]
    y = [ float(row[1]) for row in data]
    data = { 'x': x, 'y': y }
    return render_template("chart.html",result=data)

if __name__ == '__main__':
    myapp.run(host='0.0.0.0', port=port, debug=True)
