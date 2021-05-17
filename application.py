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

# I connect to the db and render the index template
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

    # Make sure the fields aren't empty
    if request.method == "POST":
        if not request.form.get("date"):
            return ("Must insert date", 400)

        if not request.form.get("name"):
            return ("Must insert name", 400)

        if not request.form.get("tickets"):
            return ("Must insert number of tickets", 400)

        #Takes the variables from the form "create_events.html" and save them in local variables
        datev = request.form.get("date")
        namev = request.form.get("name")
        ticketsv = request.form.get("tickets")

        # I connect to the db and insert the variables from the form into db to save the event created
        conn = sqlite3.connect('events.db')
        print ("Opened database successfully")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO events (date, event_name, total_tickets, tickets_redeemed) VALUES (?,?,?,0)''', (datev, namev, ticketsv))
        print("Insert done")

        # I extracted the last event_id from events table, which is a primary key, and called "create_ticket" function to create ticket tokens for that specific event id
        cursor.execute("SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1")
        # i had to parse the data type and extract the value within it
        eventid = cursor.fetchall()[0][0]
        print(eventid)
        conn.commit()
        conn.close()
        # eventid is the last event from extracted the db. We do this function call to tell how many tickets to create and for which eventid. 0 is the value of the 3rd parameter and differentiate the function call which is
        # used for "update_tickets" as well and we do not need the extra functionality from "if b == 1" which is only applied for "update_tickets"
        create_ticket(ticketsv, eventid, 0)
        return redirect("/events")

# This function creates the number of tickets for a specific event_id
def create_ticket(ticket_number, event_id, b):
    print (ticket_number)
    print(event_id)
    # I connect to the db
    conn = sqlite3.connect('events.db')

    # for each ticket create a token
    for i in range (int(ticket_number)):
        ticket_token = uuid.uuid4()
        print(i)
        print ("Opened database successfully2")
        cursor = conn.cursor()
        # save the token into the db with event_id and redeemed ticket which is 0 by default
        cursor.execute('''INSERT INTO tickets (event_id, ticket_token, redeemed_ticket) VALUES (?,?,0)''', (event_id, str(ticket_token)))
        print("Insert done2")
        conn.commit()
    # i did this to know if the function call to create_ticket comes from update_ticket
    if b == 1:
        print ("call from js")
        # after the user insert more tickets to be added to that event, i updated the total number of tickets to that event_id
        cursor.execute("SELECT total_tickets FROM events WHERE event_id=?", (event_id,))
        # i extracted it, and saved it in a local variable. cursor.fetchall() returns a list of tuple therefore i wrote [0][0] to extract the content
        tot_tickets = cursor.fetchall()[0][0]
        # updated the total tickets after user user added more
        cursor.execute("UPDATE events SET total_tickets=? WHERE event_id=?", (int(tot_tickets)+int(ticket_number), event_id))
        conn.commit()
    conn.close()

# this function displays the events using only get method.
@app.route("/events", methods = ["GET", "POST"])
def events():
    if request.method == "GET":
        # I connected to the db and displayed everything from db (event_id, date, event_name)
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()
        conn.close()
        return render_template("events.html", results=rows)

# enter the ticket token and returns OK or GONE
@app.route("/ticket_status", methods = ["GET"])
def ticket_status():
    if request.method == "GET":
        return render_template("ticket_status.html")

# after i press the button from status token (after i entered the ticket token) it will redirect me to /redeem to display OK or GONE
@app.route("/redeem", methods = ["GET"])
def token_status():
    if request.method == "GET":
        # tickets parameter from form, i need it because i need to check its status
        token = request.args.get("tickets")
        print(token)
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        # extract the status for that specific ticket
        row = cursor.execute("SELECT redeemed_ticket FROM tickets WHERE ticket_token=?", (token,))
        print(row)
        # it will return a list of tuples
        row = cursor.fetchall()
        print(row[0])
        conn.close()
        if row[0][0] == 0:
            return ("ok", 200)
        else:
            return ("GONE", 410)

# when clicking on a specific event name, in the url you can see the event id which is unique for each event
@app.route("/event/<int:event_id>", methods = ["GET"])
def event_details(event_id):
    if request.method == "GET":
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        # i extracted from db the details of that event
        cursor.execute("SELECT total_tickets, tickets_redeemed, event_name FROM events WHERE event_id=?", (event_id,))
        rows = cursor.fetchall()
        # i extracted the tokens and status of each token
        cursor.execute("SELECT ticket_token, redeemed_ticket FROM tickets WHERE event_id=?", (event_id,))
        results = cursor.fetchall()
        # display how many tickets were registered as redeemed in the db
        cursor.execute("SELECT COUNT(redeemed_ticket) FROM tickets WHERE event_id=? and redeemed_ticket=1", (event_id,))
        total_redeemed = cursor.fetchall()[0][0]
        print(results)
        conn.close()
        # row[0] because i wanted to extract the values
        return render_template("event_details.html", rows=rows[0], event_id=event_id, results=results, total_redeemed=total_redeemed)

# this function is called from js to update the event details
@app.route("/update_tickets", methods = ["POST"])
def update_tickets():
    if request.method == "POST":
        # reads the json parameters from the post request. json is a data type key value pair.
        request_data = request.get_json()
        print(request_data["new_ticket"])
        print(request_data["event_id"])
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        # i updated the events db where i update the total tickets for a specific event id
        cursor.execute("UPDATE events SET total_tickets=? WHERE event_id=?", (request_data["new_ticket"], request_data["event_id"]))
        conn.commit()
        conn.close()
        # call to create_ticket function to ceate the tokens
        create_ticket(request_data["new_ticket"], request_data["event_id"], 1)
        return "ok"

# this function prints the total number of tickets. is the second xhr request from js. for refresh button
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

