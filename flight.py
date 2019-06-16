from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from random import randint
from datetime import datetime


app = Flask(__name__)
client = MongoClient()
my_database = client["flight_system"]               # DATABASE NAME
flight_collection = my_database["flights"]           # FLIGHT COLLECTION
booking_collection = my_database["bookings"]            # BOOKING COLLECTION

@app.route("/")
def hello():
    return "Welcome to the Air India API"


@app.route("/flights/", methods=["POST","GET"])
def all_flights():
    if request.method == "GET":
        results = []
        for flight in flight_collection.find():
            results.append(flight)
        return jsonify(results)


    if request.method =="POST":
        arguments = request.args
        if not all(key in arguments for key in ("id","name","model","airline","mfg")):
            return "Invalid or incomplete data enter. Please provide id, name, model, airline, mfg"

        if "capacity" in arguments:
            capacity = arguments["capacity"]
        else:
            capacity = 100

        if flight_collection.find_one({"_id":arguments["id"]}):
            return "ERROR: Flight with this id or flight-no already exist"

        flight_collection.insert_one({
                    "_id": arguments["id"],
                    "name": arguments["name"],
                    "model": arguments["model"],
                    "airline": arguments["airline"],
                    "capacity": int(capacity),
                    "seats_booked": 0,
                    "mfg": arguments["mfg"],
                    "service": []
                })

        return "Flight successfully added."


@app.route("/flight/<string:flight_no>", methods=["GET","HEAD","PATCH","DELETE"])
def flight(flight_no):
    if request.method == 'GET':
        result = flight_collection.find_one({"_id":flight_no})
        if result:
            return jsonify(result)
        else:
            return "Flight no " + flight_no + " does not exist."

    if request.method == 'HEAD':

        result = flight_collection.find_one({"_id":flight_no})
        if result:
            return make_response(jsonify(result), 200)
        else:
            return make_response(jsonify({}),404)

    # UPDATE FLIGHT DATA
    if request.method == 'PATCH':
        data = {}
        for field in request.args:
            data[field] = request.args[field]

        result = flight_collection.find_one_and_update({"_id": flight_no},{
            "$set": data
        })

        if result:
            return "Successfully updated" + str(data)
        else:
            return "Error occured in finding the flight or flight does not exist"

    # DELETE FLIGHT
    if request.method == 'DELETE':

        result = flight_collection.find_one_and_delete({'_id':flight_no})
        if result:
            return "Successfully deleted flight no "+ flight_no
        else:
            return "Cannot find flight no "+ flight_no+ " ."


#SEAT AVAILABILITY INQUIRY
@app.route("/flight/<string:flight_no>/availability")
def booking(flight_no):
    result = flight_collection.find_one({"_id":flight_no})
    if result:
        seat_available = result["capacity"] - result["seats_booked"]
        return str(seat_available)
    else:
        return "invalid flight number"


# FOR TICKETS BOOKING IN FLIGHT
@app.route("/flight/<flight_no>/book",methods=["POST"])
def book(flight_no):
    found_flight = flight_collection.find_one({"_id":flight_no})
    if all(i in request.args for i in ("email","no_of_tickets","comment")) and found_flight:
        email = request.args["email"]
        seat_available = found_flight["capacity"] - found_flight["seats_booked"]
        no_of_tickets = int(request.args["no_of_tickets"])

        if seat_available >= no_of_tickets:
            updated_seat = found_flight["seats_booked"] + no_of_tickets
            flight_collection.update_one({"_id": flight_no},{
                "$set":{
                    "seats_booked":updated_seat
                }
            })

            # BOOOKING ID WILL BE IN FORMAT "1001-25326"
            booking_id =  flight_no + "-" + str(randint(100000,999999))

            # ADD_BOOKING FUNCTION WILL ADD DEATILS TO THE BOOKING COLLECTIONS
            add_booking(booking_id, flight_no, email, no_of_tickets, request.args["comment"])
            return booking_id

        else:
            return "Sorry, " + str(no_of_tickets) + " seats are not available."
    else:
        return "Invalid flight number OR email or total no of seats or comment not given"


# FOR BOOKING INFORMATION
@app.route("/flight/<flight_no>/book/<booking_id>")
def check_booking(flight_no, booking_id):
    flight = flight_collection.find_one({"_id":flight_no})
    booking = booking_collection.find_one({"_id":booking_id})
    if flight and booking:
        data = {}
        for field in booking:
            data[field] = booking[field]
        return jsonify(data)
    else:
        return "Either flight no or booking no Invalid"


# FOR PARTIAL OR FULL TICKETS CANCELLATION
@app.route("/cancellation", methods = ["PATCH"])
def cancellation():

    # WILL CHECK IF ALL REQUIRED ARGUMENT IS PASSED
    if all(argument in request.args for argument in ["email", "booking_id", "no_of_seats"]):
        email = request.args["email"]
        booking_id = request.args["booking_id"]
        seats_to_cancel = int(request.args["no_of_seats"])
        booking = booking_collection.find_one({"_id":booking_id})

        # WILL ONLY ALLOW TO CANCEL TICKET IF CORRECT EMAIL AND BOOKING ID PASSED IN FORM
        if booking and booking["email"] == email:
            total_tickets = booking["no_of_tickets"]
            if total_tickets > seats_to_cancel:
                booking_collection.find_one_and_update({"_id":booking_id},{
                    "$set":{
                        "no_of_tickets": total_tickets - seats_to_cancel
                    }
                })
                return str(seats_to_cancel) + " seats cancelled."

            # WILL CANCEL THE WHOLE TICKET AND DELETE THE ENTRY FROM DATABASE
            elif total_tickets == seats_to_cancel:
                booking_collection.find_one_and_delete({"_id":booking_id})
                return "Your ticket is cancelled."

            else:
                return "Unsuccessful because you are trying to cancel more tickets than you have booked"

        else:
            return "Invalid Booking ID and email combination."

    else:
        return "Please provide email, no of seats to cancel with its booking id"

# FOR ADDING SERVICE RECORD
@app.route("/service/<flight_no>", methods=["POST"])
def service(flight_no):
    if all(argument in request.args for argument in ["date_of_service","service_by"]):
        service_by = request.args["service_by"]

        date_of_service = datetime.strptime(request.args["date_of_service"], "%d-%m-%Y")


        flight = flight_collection.find_one_and_update({"_id":flight_no},{
            "$addToSet":{
                "service": {"date_of_service": date_of_service,
                            "service_by": service_by}
            }
        })
        if flight:
            return "Success in adding service record"
        else:
            return "No flight found in with this flight_id"


    else:
        return "USAGE: provide date_of_service and service_by"

def add_booking(booking_id, flight_no, email, no_of_ticket, comments):
    booking_collection.insert_one({
        "_id": booking_id,
        "flight_no": flight_no,
        "email": email,
        "no_of_tickets": no_of_ticket,
        "comments": comments
    })
