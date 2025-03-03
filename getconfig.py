#!/usr/bin/env python3

from napalm import get_network_driver
import json
from datetime import datetime

def configurations():
    driver = get_network_driver("ios")

    routers = [{"hostname": "198.51.100.1","Device":"Router (R1)", "username": "admin", "password": "admin", "platform": "ios"},
               {"hostname": "172.16.1.1","Device":"Router (R2)", "username": "admin", "password": "admin", "platform": "ios"},
               {"hostname": "172.16.1.3","Device":"Router (R4)", "username": "admin", "password": "admin", "platform": "ios"},
               {"hostname": "172.16.1.2","Device":"Router (R3)","username": "admin", "password": "admin", "platform": "ios"}]

    saved_files = [] #Initializes an empty list to store names of saved configuration files.

    for router in routers: #Starts a loop to iterate through each router in the routers list.
        try: #Begins a try-except block for error handling.
            router_conn = driver(hostname=router["hostname"], #Creates a NAPALM connection object for the current router using the driver and router information.
                                 username=router["username"],
                                 password=router["password"])
            router_conn.open() #Opens the connection to the router.
            print(f"Connecting to {router['hostname']}") #Prints a message indicating router is being connected
            output = router_conn.get_config()["running"] #Retrieves the running configuration of the router and stores it in output.
            router_conn.close() #Closes the connection to the router.

            timestamp = datetime.utcnow().strftime('%Y-%m-%d T %H-%M-%S') #Generates a timestamp string in the format 'YYYY-MM-DD T HH-MM-SS'
            filename = f"{router['Device']}:{router['hostname']}-{router['platform']}-->{timestamp}.txt" #Creates a filename string using router information and the timestamp.

            with open(filename, "w") as file: #Opens a new file with the generated filename and writes the router configuration to it.
                file.write(output)

            print(f"Config file is saved as: {filename}") #Prints a message indicating the name of the saved configuration file.
            saved_files.append(filename) #Adds the filename to the saved_files list

        except Exception as e:
            print(f"Failed to get config: {e}")

    return saved_files #Returns the list of saved configuration filenames

if __name__ == "__main__":
    configurations()
