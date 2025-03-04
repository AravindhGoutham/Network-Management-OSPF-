#!/usr/bin/env python3

import napalm
import sqlite3

ROUTER_1 = { #router 1 credentials
    "hostname": "198.51.100.1",
    "username": "admin",
    "password": "admin",
}

def get_loopback_ips(): #This function is defined to retrieve loopback IP addresses from a database.
    try: #These lines establish a connection to database "database.db" and create a cursor object.
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT loopback_ip FROM users")
        loopback_ips = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close() #This closes the database connection and returns the list of loopback IPs.
        return loopback_ips
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return [] #If a database error occurs, it prints the error and returns an empty list.

def ping_from_router(router, ip): #This function is defined to ping an IP address from router 1.
    driver = napalm.get_network_driver("ios") 
    device = driver(    #This creates a device object using the router details provided.
        hostname=router["hostname"], 
        username=router["username"], 
        password=router["password"]
    )

    try:
        device.open() #This open a connection to the device.
        print(f"Connected to {router['hostname']} - Executing ping to {ip}")
        ping_result = device.ping(destination=ip, count=2)  # This line executes a ping command from the router to the specified IP address, sending 2 packets.
        device.close() #This closes the connection to the device.
        
        if ping_result.get("success", {}): #This checks the ping result and returns a success or failure message.
            return f"Ping to {ip} - Successful"
        else:
            return f"Ping to {ip} - Failed"

    except Exception as e:
        return f"Error pinging {ip} from {router['hostname']}: {e}"

def perform_ping_test(): #This function is defined to perform ping tests on IPs fetched from the database.
    loopback_ips = get_loopback_ips() #This gets the loopback IPs and returns a message if none are found.
    if not loopback_ips: 
        return ["No loopback IPs found in the database."]

    results = [ping_from_router(ROUTER_1, ip) for ip in loopback_ips]
    return results #This pings each IP address from ROUTER_1 and returns the results

if __name__ == "__main__":
    results = perform_ping_test()
    for result in results:
        print(result)
