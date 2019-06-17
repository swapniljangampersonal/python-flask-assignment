from flask import Flask, render_template, request
#from flask_mysqldb import MySQL
import os
myapp = Flask(__name__)

# myapp.config['MYSQL_HOST'] = 'swapnil-jangam-server.database.windows.net'
# myapp.config['MYSQL_USER'] = 'swapniljangam@swapnil-jangam-server'
# myapp.config['MYSQL_PASSWORD'] = 'Kingarhur4'
# myapp.config['MYSQL_DB'] = 'mydatabase'

# mysql = MySQL(myapp)
port = int(os.getenv("PORT", 5000))

# def get_connection():
#     return mysql.connection

@myapp.route("/")
def hello():
    # conn = get_connection()
    res = ''
    # if not conn:
    #     res = 'No connection to db'
    # else:
    #     res = 'DB connected'
    return render_template("static/index.html", result=res)

# @myapp.route('/delete', methods=['GET'])
# def deleteall():
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("DELETE FROM earthquake")
#     conn.commit()
#     cur.close()
#     return "Successfully deleted all data"

# if __name__ == '__main__':
#     myapp.run(host='0.0.0.0', port=port, debug=True)
