from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import os, csv, math
import dateutil.parser
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from timezonefinder import TimezoneFinder
import random
import redis
import hashlib
import pickle
import numpy

myapp = Flask(__name__)

myapp.config['MYSQL_HOST'] = 'swapnilserver.mysql.database.azure.com'
myapp.config['MYSQL_USER'] = 'swapniljangam@swapnilserver'
myapp.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
myapp.config['MYSQL_DB'] = os.environ['MYSQL_DB']

mysql = MySQL(myapp)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
port = int(os.getenv("PORT", 5000))

r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=6379, db=0, password=os.environ['REDIS_PASS'])
r.flushall()
def get_connection():
    return mysql.connection

@myapp.route("/")
def hello():
    return render_template("index.html")

@myapp.route('/create-table')
def createTable():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("Drop table earthquake")
    conn.commit()
    start_time = datetime.now()
    cur.execute("create table earthquake (time datetime, latitude DECIMAL(20, 15), longitude DECIMAL(20, 15),depth DECIMAL(40, 20),mag DECIMAL(40, 20),net varchar(10),id varchar(50),place varchar(200));")
    conn.commit()
    end_time = datetime.now()
    total_time = end_time - start_time
    return "Created table in " + str(total_time.total_seconds()) + " secs"

@myapp.route('/random-queries')
def get_random_queries():
    conn = get_connection()
    cur = conn.cursor()
    start_time = datetime.now()
    for x in range(1000):
        sql = "SELECT * FROM earthquake WHERE mag = "+ str(round(random.uniform(1.2, 8.0), 1))
        hash = hashlib.sha224(sql.encode('utf-8')).hexdigest()
        key = "sql_cache:" + hash
        cur.execute(sql)
        data = cur.fetchall()
        if r.get(key) is None:
            r.set(key, pickle.dumps(data))
    end_time = datetime.now()
    total_time = end_time - start_time
    return "Random 1000 queries executed in " + str(total_time.total_seconds()) + " secs"

@myapp.route('/unrestricted-random-queries')
def unrestricted_random_queries():
    queries = [
        "SELECT * FROM earthquake WHERE mag BETWEEN "+ str(round(random.uniform(1.2, 8.0), 3)) +" AND " + str(round(random.uniform(1.2, 8.0), 3)),
        "SELECT * FROM earthquake WHERE SUBSTRING_INDEX(place, ',', 1)='CA'"
    ]
    conn = get_connection()
    cur = conn.cursor()
    start_time = datetime.now()
    for x in range(1000):
        sql = queries[random.randint(0,len(queries) - 1)]
        hash = hashlib.sha224(sql.encode('utf-8')).hexdigest()
        key = "sql_cache:" + hash
        cur.execute(sql)
        data = cur.fetchall()
        if r.get(key) is None:
            r.set(key, pickle.dumps(data))
    end_time = datetime.now()
    total_time = end_time - start_time
    return "Restricted random 1000 queries executed in " + str(total_time.total_seconds()) + " secs"

@myapp.route('/random-queries-cached')
def get_random_queries_cached():
    conn = get_connection()
    cur = conn.cursor()
    start_time = datetime.now()
    for x in range(1000):
        sql = "SELECT * FROM earthquake WHERE mag = "+ str(round(random.uniform(1.2, 8.0), 1))
        hash = hashlib.sha224(sql.encode('utf-8')).hexdigest()
        key = "sql_cache:" + hash
        # Check if data is in cache.
        if (r.get(key)):
            continue
        else:
            # Do MySQL query   
            cur.execute(sql)
            data = cur.fetchall()
            r.set(key, pickle.dumps(data))
    r.flushall()
    end_time = datetime.now()
    total_time = end_time - start_time
    return "Random 1000 queries executed in " + str(total_time.total_seconds()) + " secs"

@myapp.route('/unrestricted-random-queries-cached')
def unrestricted_random_queries_cached():
    queries = [
        "SELECT * FROM earthquake WHERE mag BETWEEN "+ str(round(random.uniform(1.2, 8.0), 3)) +" AND " + str(round(random.uniform(1.2, 8.0), 3)),
        "SELECT * FROM earthquake WHERE SUBSTRING_INDEX(place, ',', 1)='CA'"
    ]
    conn = get_connection()
    cur = conn.cursor()
    start_time = datetime.now()
    for x in range(1000):
        sql = queries[random.randint(0,len(queries) - 1)]
        hash = hashlib.sha224(sql.encode('utf-8')).hexdigest()
        key = "sql_cache:" + hash
        
        # Check if data is in cache.
        if (r.get(key)):
            continue
        else:
            # Do MySQL query   
            cur.execute(sql)
            data = cur.fetchall()
            r.set(key, pickle.dumps(data))
    r.flushall()
    end_time = datetime.now()
    total_time = end_time - start_time
    return "Restricted random 1000 queries executed in " + str(total_time.total_seconds()) + " secs"

@myapp.route('/clear-cache', methods=['GET'])
def earthquakes():
    r.flushall()
    return "Cache cleared"

@myapp.route('/earthquake', methods=['GET'])
def clearcache():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM earthquake")
    res = cur.fetchall()
    return render_template("test.html", result=res)

@myapp.route('/delete', methods=['GET'])
def deleteall():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM earthquake")
    conn.commit()
    cur.close()
    return "Successfully deleted all data"

@myapp.route('/latrange', methods=['GET'])
def getlatrange():
    conn = get_connection()
    cur = conn.cursor()
    latFrom = request.args['latFrom']
    latTo = request.args['latTo']
    cur.execute("SELECT place, time, mag from earthquake WHERE latitude BETWEEN "+ str(latFrom) +" AND "+ str(latTo))
    res = cur.fetchall()
    return render_template("test.html", result=res)

@myapp.route('/csv', methods=['POST'])
def upload_csv():
    file = request.files['csvFile']
    target = os.path.join(APP_ROOT, 'static')
    file.save(os.path.join(target, file.filename))
    f = open(os.path.join(target, file.filename), "r")
    reader = csv.DictReader( f, fieldnames = ( "time","latitude","longitude","depth","mag","net","id","place"))
    conn = get_connection()
    cur = conn.cursor()
    next(reader, None)
    for row in reader:
        latitude = row['latitude'] if row['latitude'] else float(0)
        longitude = row['longitude'] if row['longitude'] else float(0)
        mytime = dateutil.parser.parse(row['time'])
        mytime = get_timezone_date(row['longitude'], row['latitude'], mytime.strftime("%Y-%m-%d %H:%M:%S.%f"))
        depth = row['depth'] if row['depth'] else float(0)
        mag = row['mag'] if row['mag'] else float(0)
        # magType = row["magType"] if row["magType"] else ''
        # nst = row["nst"] if row["nst"] else 0
        # gap = row["gap"] if row["gap"] else float(0)
        # dmin = row["dmin"] if row["dmin"] else 0
        # rms = row["rms"] if row["rms"] else float(0)
        net = row["net"] if row["net"] else ''
        earthquake_id = row["id"] if row["id"] else ''
        # updated = row["updated"] if row["updated"] else ''
        place = row["place"] if row["place"] else ''
        # earthquake_type = row["type"] if row["type"] else ''
        # horizontalError = row["horizontalError"] if row["horizontalError"] else 0
        # depthError = row["depthError"] if row["depthError"] else 0
        # magError = row["magError"] if row["magError"] else 0
        # magNst = row["magNst"] if row["magNst"] else 0
        # status = row["status"] if row["status"] else ''
        # locationSource = row["locationSource"] if row["locationSource"] else ''
        # magSource = row["magSource"] if row["magSource"] else ''
        rad_lat = float(row['latitude'])
        rad_long = float(row['longitude'])
        cos_lat = math.cos(rad_lat * math.pi / 180)
        sin_lat = math.sin(rad_lat * math.pi / 180)
        cos_long = math.cos(rad_long * math.pi / 180)
        sin_long = math.sin(rad_long * math.pi / 180)
        cur.execute("INSERT INTO earthquake VALUES ('"+ mytime +"', "+ str(latitude)+", "+str(longitude)+", "+str(depth)+", "+str(mag)+", '"+str(net)+"', '"+str(earthquake_id)+"', %s" + ");",[place])
        conn.commit()
    cur.close()
    return render_template("first.html")

@myapp.route('/checklat', methods=['GET'])
def checklat():
    return render_template("first.html")

@myapp.route('/checklattimes', methods=['GET'])
def checklattimes():
    return render_template("second.html")

@myapp.route('/latrangetimes', methods=['GET'])
def getlatrangetimes():
    conn = get_connection()
    cur = conn.cursor()
    latFrom = request.args['latFrom']
    latTo = request.args['latTo']
    my_range = numpy.arange(float(latFrom), float(latTo), 0.8)
    rangelist = []
    i = 0
    while i < len(my_range):
        if(i+1 >= len(my_range)):
            break
        rangelist.append(my_range[i], my_range[i+1])
    times = request.args['times']
    times = int(times)
    resultlist = []
    for x in range(times):
        ind = random.randint(0,len(rangelist) - 1) 
        start_time = datetime.now()
        cur.execute("SELECT count(*) from earthquake WHERE latitude BETWEEN "+ rangelist[ind][0] +" AND "+ rangelist[ind][1])
        end_time = datetime.now()
        total_time = end_time - start_time
        res = cur.fetchall()
        resultlist.append(res[0], total_time.total_seconds(), rangelist[ind][0], rangelist[ind][1])
    return render_template("test.html", result=resultlist)

def get_timezone_date(longitude, latitude, dt):
    tf = TimezoneFinder()
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    datetime_obj_naive = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
    mytimezone = tf.timezone_at(lng=float(longitude), lat=float(latitude))
    if not mytimezone:
        return datetime_obj_naive.strftime(fmt)[:-3]
    utcmoment = datetime_obj_naive.replace(tzinfo=pytz.utc)
    localDatetime = utcmoment.astimezone(pytz.timezone(str(mytimezone)))
    return localDatetime.strftime(fmt)[:-3]

# if __name__ == '__main__':
#     myapp.run(host='0.0.0.0', port=port, debug=True)
