from flask import Flask, render_template
myapp = Flask(__name__)

@myapp.route("/")
def hello():
    return "test"