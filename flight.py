from flask import Flask, request, jsonify, make_response, json
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
    return make_response(jsonify({}),200)


@app.route("/flights/", methods=["POST","GET"])
def all_flights():
    raw_data = json.loads(request.data)

    if request.method == "GET":
        results = []
        for flight in flight_collection.find():
            results.append(flight)
        return jsonify(results)


    if request.method =="POST":
        arguments = raw_data
        if not all(key in arguments for key in ("id","name","model","airline","mfg")):
            return make_response(jsonify({"response":"Invalid or incomplete data enter. Please provide id, name, model, airline, mfg"}),400)

        if "capacity" in arguments:
            capacity = arguments["capacity"]
        else:
            capacity = 100

        if flight_collection.find_one({"_id":arguments["id"]}):
            return make_response(jsonify({"response":"Flight with this id or flight-no already exist"}),400)

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

        return make_response(jsonify({"response":"Flight successfully added."}),200)


@app.route("/flight/<string:flight_no>", methods=["GET","HEAD","PATCH","DELETE"])
def flight(flight_no):
    if request.method == 'GET':
        result = flight_collection.find_one({"_id":flight_no})
        if result:
            return make_response(jsonify(result),200)
        else:
            to_send = "Flight no " + flight_no + " does not exist."
            return make_response(jsonify({"response": to_send}),404)

    if request.method == 'HEAD':

        result = flight_collection.find_one({"_id":flight_no})
        if result:
            return make_response(jsonify(result), 200)
        else:
            return make_response(jsonify({}),404)

    # UPDATE FLIGHT DATA
    if request.method == 'PATCH':
        raw_data = json.loads(request.data)

        data = {}
        for field in raw_data:
            data[field] = raw_data[field]

        result = flight_collection.find_one_and_update({"_id": flight_no},{
            "$set": data
        })

        if result:
            to_send = "Successfully updated" + str(data)
            return make_response(jsonify({"response":to_send}),200)
        else:
            to_send = "Error occured in finding the flight or flight does not exist"
            return make_response(jsonify({"response":to_send}),404)

    # DELETE FLIGHT
    if request.method == 'DELETE':

        result = flight_collection.find_one_and_delete({'_id':flight_no})
        if result:
            to_send = "Successfully deleted flight no "+ flight_no
            return make_response(jsonify({"response":to_send}),200)
        else:
            to_send =  "Cannot find flight no "+ flight_no+ " ."
            return make_response(jsonify({"response":to_send}),404)


#SEAT AVAILABILITY INQUIRY
@app.route("/flight/<string:flight_no>/availability")
def booking(flight_no):
    result = flight_collection.find_one({"_id":flight_no})
    if result:
        seat_available = result["capacity"] - result["seats_booked"]
        return make_response(jsonify({"seat available":seat_available}),200)
    else:
        to_send =  "invalid flight number"
        return make_response(jsonify({"response":to_send}),404)



# FOR TICKETS BOOKING IN FLIGHT
@app.route("/flight/<flight_no>/book",methods=["POST"])
def book(flight_no):
    found_flight = flight_collection.find_one({"_id":flight_no})
    raw_data = json.loads(request.data)

    if all(i in raw_data for i in ("email","no_of_tickets","comment")) and found_flight:
        email = raw_data["email"]
        seat_available = found_flight["capacity"] - found_flight["seats_booked"]
        no_of_tickets = int(raw_data["no_of_tickets"])

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
            add_booking(booking_id, flight_no, email, no_of_tickets, raw_data["comment"])
            return booking_id

        else:
            to_send =  "Sorry, " + str(no_of_tickets) + " seats are not available."
            return make_response(jsonify({"response":to_send}),200)

    else:
        to_send =  "Invalid flight number OR email or total no of seats or comment not given"
        return make_response(jsonify({"response":to_send}),400)



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
        to_send =  "Either flight no or booking no Invalid"
        return make_response(jsonify({"response":to_send}),400)



# FOR PARTIAL OR FULL TICKETS CANCELLATION
@app.route("/cancellation", methods = ["PATCH"])
def cancellation():
    raw_data = json.loads(request.data)
    # WILL CHECK IF ALL REQUIRED ARGUMENT IS PASSED
    if all(argument in raw_data for argument in ["email", "booking_id", "no_of_seats"]):
        email = raw_data["email"]
        booking_id = raw_data["booking_id"]
        seats_to_cancel = int(raw_data["no_of_seats"])
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
                to_send =  str(seats_to_cancel) + " seats cancelled."
                return make_response(jsonify({"response":to_send}),200)


            # WILL CANCEL THE WHOLE TICKET AND DELETE THE ENTRY FROM DATABASE
            elif total_tickets == seats_to_cancel:
                booking_collection.find_one_and_delete({"_id":booking_id})
                to_send = "Your ticket is cancelled."
                return make_response(jsonify({"response":to_send}),200)
            else:
                to_send = "Unsuccessful because you are trying to cancel more tickets than you have booked"
                return make_response(jsonify({"response":to_send}),400)


        else:
            to_send = "Invalid Booking ID and email combination."
            return make_response(jsonify({"response":to_send}),403)
    else:
        to_send = "Please provide email, no of seats to cancel with its booking id"
        return make_response(jsonify({"response":to_send}),403)


# FOR ADDING SERVICE RECORD
@app.route("/service/<flight_no>", methods=["POST"])
def service(flight_no):
    # CONVERT request.data TO DICT USING json.loads
    raw_data = json.loads(request.data)
    if all(argument in raw_data for argument in ["date_of_service","service_by"]):
        service_by = raw_data["service_by"]

        date_of_service = datetime.strptime(raw_data["date_of_service"], "%d-%m-%Y")


        flight = flight_collection.find_one_and_update({"_id":flight_no},{
            "$addToSet":{
                "service": {"date_of_service": date_of_service,
                            "service_by": service_by}
            }
        })
        if flight:
            to_send = "Success in adding service record"
            return make_response(jsonify({"response":to_send}),200)
        else:
            to_send = "No flight found in with this flight_id"
            return make_response(jsonify({"response":to_send}),404)
    else:
        to_send = "USAGE: provide date_of_service and service_by"
        return make_response(jsonify({"response":to_send}),400)


def add_booking(booking_id, flight_no, email, no_of_ticket, comments):
    booking_collection.insert_one({
        "_id": booking_id,
        "flight_no": flight_no,
        "email": email,
        "no_of_tickets": no_of_ticket,
        "comments": comments
    })
