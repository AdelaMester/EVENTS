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

    if request.method == "POST":
        if not request.form.get("date"):
            return ("Must insert date", 400)

        if not request.form.get("name"):
            return ("Must insert name", 400)

        if not request.form.get("tickets"):
            return ("Must insert number of tickets", 400)

        datev = request.form.get("date")
        namev = request.form.get("name")
        ticketsv = request.form.get("tickets")

        conn = sqlite3.connect('events.db')
        print ("Opened database successfully")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO events (date, event_name, total_tickets) VALUES (?,?,?)''', (datev, namev, ticketsv))
        print("Insert done")
        conn.commit()
        return redirect("/events")

@app.route("/events", methods = ["GET", "POST"])
def events():
    if request.method == "GET":
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()
        return render_template("events.html", results=rows)

@app.route("/ticket_status", methods = ["GET"])
def ticket_status():
    if request.method == "GET":
        return render_template("ticket_status.html")

@app.route("/event/<int:event_id>", methods = ["GET"])
def event_details(event_id):
    if request.method == "GET":
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        print(event_id)
        cursor.execute("SELECT total_tickets, tickets_redeemed, event_name FROM events WHERE event_id=?", (event_id,))
        rows = cursor.fetchall()
        print(rows[0])
        print(rows[0][0])
        return render_template("event_details.html", rows=rows[0])



