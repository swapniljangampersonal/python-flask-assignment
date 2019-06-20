from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import os, csv, math
import html,json

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

@myapp.route('/percentvoted', methods=['GET'])
def get_percent_queries():
    conn = get_connection()
    cur = conn.cursor()
    perFrom = request.args['perFrom']
    perTo = request.args['perTo']
    group = request.args['group']
    my_range = range(int(perFrom), int(perTo), int(group))
    i = 0
    rangelist = []
    while(i < len(my_range)):
        if(i+1 >= len(my_range)):
            break
        rangelist.append([my_range[i], my_range[i+1]])
        i = i + 1
    x = []
    y = []
    for ind in range(int(group)+1):
        sql = "SELECT SUM(PercentVote) FROM voting WHERE PercentVote BETWEEN "+str(rangelist[ind][0]) +" AND "+ str(rangelist[ind][1])
        cur.execute(sql)
        data = cur.fetchone()
        x.append(str(rangelist[ind][0])+"-"+str(rangelist[ind][1]))
        y.append(float(data[0]) if data[0] else 0)
    data = { 'x': x, 'y': y }
    print(data)
    return render_template("chart.html",result=data)

if __name__ == '__main__':
    myapp.run(host='0.0.0.0', port=port, debug=True)
