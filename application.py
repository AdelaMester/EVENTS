from flask import Flask, redirect, render_template, request
import sqlite3


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods = ["GET"])
def index():
    if request.method == "GET":
        conn = sqlite3.connect('events.db')
        print ("Opened database successfully");
        conn.close()
        return render_template("index.html")

@app.route("/create_event", methods = ["GET", "POST"])
def create_event():
    if request.method == "GET":
        return render_template("create_event.html")