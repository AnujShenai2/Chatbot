# Chatbot
Contains the main chat file along with its dependencies

1. db.py -
This file handles the database connection to MySQL. It contains a function connect_db that establishes a connection to the specified database using the provided credentials. Two database connections are initialized: one for car_detail_db (containing car details like make, model, variant, etc.) and another for car_part_spares_db (containing parts and categories). If the connection fails, the program exits.


