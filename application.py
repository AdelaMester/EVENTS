from flask import Flask, redirect, render_template, request
import sqlite3
import uuid

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
        cursor.execute('''INSERT INTO events (date, event_name, total_tickets, tickets_redeemed) VALUES (?,?,?,0)''', (datev, namev, ticketsv))
        print("Insert done")
        cursor.execute("SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1")
        eventid = cursor.fetchall()[0][0]
        print(eventid)
        conn.commit()
        conn.close()
        create_ticket(ticketsv, eventid, 0)
        return redirect("/events")


def create_ticket(ticket_number, event_id, b):
    print (ticket_number)
    print(event_id)
    conn = sqlite3.connect('events.db')
    for i in range (int(ticket_number)):
        ticket_token = uuid.uuid4()
        print(i)
        print ("Opened database successfully2")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO tickets (event_id, ticket_token, redeemed_ticket) VALUES (?,?,0)''', (event_id, str(ticket_token)))
        print("Insert done2")
        conn.commit()
    if b == 1:
        print ("call from js")
        cursor.execute("SELECT total_tickets FROM events WHERE event_id=?", (event_id,))
        tot_tickets = cursor.fetchall()[0][0]
        cursor.execute("UPDATE events SET total_tickets=? WHERE event_id=?", (int(tot_tickets)+int(ticket_number), event_id))
        conn.commit()
    conn.close()


@app.route("/events", methods = ["GET", "POST"])
def events():
    if request.method == "GET":
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()
        conn.close()
        return render_template("events.html", results=rows)


@app.route("/ticket_status", methods = ["GET"])
def ticket_status():
    if request.method == "GET":
        return render_template("ticket_status.html")


@app.route("/redeem", methods = ["GET"])
def token_status():
    if request.method == "GET":
        token = request.args.get("tickets")
        print(token)
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        row = cursor.execute("SELECT redeemed_ticket FROM tickets WHERE ticket_token=?", (token,))
        print(row)
        row = cursor.fetchall()
        print(row[0])
        conn.close()
        if row[0][0] == 0:
            return ("ok", 200)
        else:
            return ("GONE", 410)


@app.route("/event/<int:event_id>", methods = ["GET"])
def event_details(event_id):
    if request.method == "GET":
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute("SELECT total_tickets, tickets_redeemed, event_name FROM events WHERE event_id=?", (event_id,))
        rows = cursor.fetchall()
        cursor.execute("SELECT ticket_token, redeemed_ticket FROM tickets WHERE event_id=?", (event_id,))
        results = cursor.fetchall()
        cursor.execute("SELECT COUNT(redeemed_ticket) FROM tickets WHERE event_id=? and redeemed_ticket=1", (event_id,))
        total_redeemed = cursor.fetchall()[0][0]
        print(results)
        conn.close()
        return render_template("event_details.html", rows=rows[0], event_id=event_id, results=results, total_redeemed=total_redeemed)


@app.route("/update_tickets", methods = ["POST"])
def update_tickets():
    if request.method == "POST":
        request_data = request.get_json()
        print(request_data["new_ticket"])
        print(request_data["event_id"])
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET total_tickets=? WHERE event_id=?", (request_data["new_ticket"], request_data["event_id"]))
        conn.commit()
        conn.close()
        create_ticket(request_data["new_ticket"], request_data["event_id"], 1)
        return "ok"


@app.route("/total_tickets", methods = ["GET"])
def total_tickets():
    if request.method == "GET":
        event_id = request.args.get("event_id")
        print(event_id)
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        total_tickets = cursor.execute("SELECT COUNT(ticket_token) FROM tickets WHERE event_id=?", (event_id,))
        total_tickets = (total_tickets.fetchall()[0][0])
        print(total_tickets)
        conn.commit()
        conn.close()
        return str(total_tickets)

