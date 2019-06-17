from flask import Flask, render_template, request
from flask_mysqldb import MySQL
myapp = Flask(__name__)

myapp.config['MYSQL_HOST'] = 'swapnil-jangam-server.database.windows.net'
myapp.config['MYSQL_USER'] = 'swapniljangam'
myapp.config['MYSQL_PASSWORD'] = 'Kingarhur4'
myapp.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(myapp)

def get_connection():
    return mysql.connection

@myapp.route("/")
def hello():
    conn = get_connection()
    res = ''
    if not conn:
        res = 'No connection to db'
    else:
        res = 'DB connected'
    return render_template("static/index.html", result=res)

@myapp.route('/delete', methods=['GET'])
def deleteall():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM earthquake")
    conn.commit()
    cur.close()
    return "Successfully deleted all data"