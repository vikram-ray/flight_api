from flask import Flask
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
try:
    client = MongoClient()
    print("DB connected Successfully")
except:
    print("Could not connect to Database")

my_database = client["flight_system"]               # DATABASE NAME
flight_collection = my_database["flights"]           # FLIGHT COLLECTION
booking_collection = my_database["bookings"]            # BOOKING COLLECTION


#QUERY ONE
print("1. Flights whose model is 737\n")
model = "737"
flight = flight_collection.find_one({"model":model})
if flight:
    print(flight)
else:
    print("No flight with model " + model + " found.")


#QUERY 2
to_find = 40
print("\n\n\n2.All Flights whose capacity is "+ str(to_find) +" and above\n")
results = flight_collection.find({"capacity":{"$gte": to_find}})

for i in results:
    print(i)


# QUERY 3
print("\n\n\n3.All flights whose service happend 5 or more months back.\n")

months = 5
past_date = datetime.today() - timedelta(days=30*months)   # 5 MONTHS FROM NOW

past_serviced_flight = flight_collection.find({"service.date_of_service":{"$lte":past_date}})

for each_flight in past_serviced_flight:
    print(each_flight)


#QUERY 4
print("\n\n\n4. Which flight was services more.\n")
all_flights = flight_collection.find({})                #FIND ALL FLIGHT
max = 0
max_serviced_flight = ""
for flight in all_flights:
    if len(flight["service"]) > max:                   #ASSIGN HIGHEST NO OF SERVICED FLIGHT
        max = len(flight["service"])                    # WITH ITS ID
        max_serviced_flight = flight["_id"]

# FIND THE FLIGHT WITH MAX_SERVICE FLIGHT_ID
print(flight_collection.find_one({"_id":max_serviced_flight}))

#QUERY 5
print("\n\n\n5. Which Service Team work is most lousy?\n")
all_flights = flight_collection.find({})
data = []
for flight in all_flights:
    data.append(flight)

min = datetime.now() - datetime.strptime("01-01-1970", "%d-%m-%Y")
lousy_team = ""
flight_no = ""

for flight in data:
    service = flight["service"]
    for i in range(len(service)-1):

        #THIS CODE WILL TRACK THE DIFF BETWEEN THIS AND PREVIOUS SERVICE
        time_diff = abs(service[i+1]["date_of_service"] - service[i]["date_of_service"])
        if time_diff < min:
            min = time_diff
            lousy_team = service[i]["service_by"]
            flight_no = flight["_id"] + " - " + flight["name"]
print("Most lousy service team is \"" + lousy_team + "\" whose service last only for " + str(min.days) + " days in flight "+ flight_no+ ".")
