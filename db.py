import mysql.connector

def connect_db(db_name):
    try:
        conn = mysql.connector.connect(host="127.0.0.1", user="root", password=" ***** ", database=db_name)
        print(f"Connected to {db_name}")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to {db_name}: {err}")
        return None

# Connect to databases
db_connection_1 = connect_db("car_detail_db")
db_connection_2 = connect_db("car_part_spares_db")
if not (db_connection_1 and db_connection_2):
    exit()

cursor_1 = db_connection_1.cursor()
cursor_2 = db_connection_2.cursor()
