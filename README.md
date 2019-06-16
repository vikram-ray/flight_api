# flight_api
FLIGHT API using FLASK 

THIS IS A FLIGHT API WHICH WAS MADE AS A ASSIGNMENT

FOLLOWING END POINTS:
GET: /flights     : Returns all the flights

GET: /flight/<flight_no>   : Returns specific flight data

HEAD: /flight/<flight_no> : Check if flight exist 

POST /flights      : Add new flight. Each flight must have atleast total
seats. 

PATCH /flight/<flight_no> : Update flight data

DELETE /flight/<flight_no>

Booking management:

GET: /flight/<flight_no>/availability  : must return the number of seats
available. 

POST:  /flight/<flight_no>/book  : In payload you should atleast pass
number of seats and booking person's contact email. Response must return a
unique booking_id.

GET: /flight/<flight_no>/book/<booking_id>  : Get booking information.

Booking records should also be maintained in a separate collection.  

Support Partial/full booking cancellation using PATCH/DELETE end points.
Use your creativity. In payload, you should pass number of seats to be
released. This should update the booked seats in db. If the all seats are
released, booking get totally canceled and entry is removed from DB. But
if only few seats are released, we just update the DB entry with remaining
seats.  


QUERIES: 
1. Flights whose model is 737 
2. All Flights whose capacity is X and above 
3. All flights whose service happend 5 or more months back 
4. which flight was services more 
5. Which Service Team work is most lousy 

MY OUTPUT AFTER RUNNING query.py 
1. Flights whose model is 737

{'_id': '1001', 'name': 'Air India 2', 'model': '737', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 0, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2017, 5, 21, 0, 0), 'service_by': 'VermaJI Cleaner'}]}



2.All Flights whose capacity is 40 and above

{'_id': '1001', 'name': 'Air India 2', 'model': '737', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 0, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2017, 5, 21, 0, 0), 'service_by': 'VermaJI Cleaner'}]}
{'_id': '1002', 'name': 'SyScraper Metro', 'model': 'SyScraper', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 5, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2018, 4, 16, 0, 0), 'service_by': 'Mr Prasad and sons'}, {'date_of_service': datetime.datetime(2019, 5, 16, 0, 0), 'service_by': 'Mr Prasad and sons'}, {'date_of_service': datetime.datetime(2019, 5, 20, 0, 0), 'service_by': 'DareDevils Cleaner'}]}
{'_id': '1003', 'name': 'SyScraper Urban', 'model': 'SyScraper', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 0, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2019, 5, 20, 0, 0), 'service_by': 'Sunrisers Cleaner'}, {'date_of_service': datetime.datetime(2019, 5, 21, 0, 0), 'service_by': 'VermaJI Cleaner'}]}



3.All flights whose service happend 5 or more months back.

{'_id': '1001', 'name': 'Air India 2', 'model': '737', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 0, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2017, 5, 21, 0, 0), 'service_by': 'VermaJI Cleaner'}]}
{'_id': '1002', 'name': 'SyScraper Metro', 'model': 'SyScraper', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 5, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2018, 4, 16, 0, 0), 'service_by': 'Mr Prasad and sons'}, {'date_of_service': datetime.datetime(2019, 5, 16, 0, 0), 'service_by': 'Mr Prasad and sons'}, {'date_of_service': datetime.datetime(2019, 5, 20, 0, 0), 'service_by': 'DareDevils Cleaner'}]}



4. Which flight was services more.

{'_id': '1002', 'name': 'SyScraper Metro', 'model': 'SyScraper', 'airline': 'AirIndia', 'capacity': 50, 'seats_booked': 5, 'mfg': '13-2-2019', 'service': [{'date_of_service': datetime.datetime(2018, 4, 16, 0, 0), 'service_by': 'Mr Prasad and sons'}, {'date_of_service': datetime.datetime(2019, 5, 16, 0, 0), 'service_by': 'Mr Prasad and sons'}, {'date_of_service': datetime.datetime(2019, 5, 20, 0, 0), 'service_by': 'DareDevils Cleaner'}]}



5. Which Service Team work is most lousy?

Most lousy service team is "Sunrisers Cleaner" whose service last only for 1 days in flight 1003 - SyScraper Urban.
