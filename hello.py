from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import os, csv, math
import html,json
import numpy

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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT (StateName) from voting where TotalPop between 5000 and 10000")
    res = cur.fetchall()
    print(res)
    cur.execute("SELECT (StateName) from voting where TotalPop between 10000 and 50000")
    res2 = cur.fetchall()
    print(res2)
    return render_template("index.html", result1=res, result2=res2)



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

@myapp.route('/formula', methods=['GET'])
def formula():
    n1 = request.args['n1']
    n2 = request.args['n2']
    xlist = []
    ylist = []
    for y in range(int(n1), int(n2)):
        x = y*y+1
        xlist.append(x)
        ylist.append(y)
    data = { 'x': xlist, 'y': ylist }
    return render_template("chart2.html",result=data)

@myapp.route('/percentvoted', methods=['GET'])
def get_percent_queries():
    conn = get_connection()
    cur = conn.cursor()
    perFrom = "40"
    perTo = "80"
    group = request.args['group']
    my_range = numpy.arange(int(perFrom), int(perTo), int(group))
    my_range = list(chunks(range(int(perFrom), int(perTo)), int(group)))
    x = []
    y = []
    for myra in my_range:
        sql = "SELECT SUM(Voted/TotalPop)*100 FROM voting WHERE (Voted/TotalPop)*100 BETWEEN "+str(myra[0]) +" AND "+ str(myra[len(myra)-1]+1)
        cur.execute(sql)
        data = cur.fetchone()
        x.append(str(myra[0])+"-"+str(myra[len(myra)-1]+1))
        y.append(float(data[0]) if data[0] else 0)
    data = { 'x': x, 'y': y }
    return render_template("chart.html",result=data)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

if __name__ == '__main__':
    myapp.run(host='0.0.0.0', port=port, debug=True)
