from flask import Flask, render_template, request
import sqlite3
import os
myapp = Flask(__name__)

def get_connection():
    return sqlite3.connect('static/earth.db')

port = int(os.getenv("PORT", 5000))

@myapp.route("/")
def hello():
    conn = get_connection()
    res = 'Hi'
    if not conn:
        res = 'No connection to db'
    else:
        res = 'DB connected'
    return render_template("index.html", result=res)

@myapp.route('/delete', methods=['GET'])
def deleteall():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM earthquake")
    conn.commit()
    cur.close()
    return "Successfully deleted all data"

# if __name__ == '__main__':
#     myapp.run(host='0.0.0.0', port=port, debug=True)
