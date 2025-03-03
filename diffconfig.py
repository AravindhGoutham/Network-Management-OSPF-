#!/usr/bin/env python3

import os
import napalm

CONFIG_DIR = "."
#This line defines a variable CONFIG_DIR and sets it to ".", which represents the current directory. This is where the script will look for saved configuration files.
ROUTER_CREDENTIALS = {
    "R1": {"hostname": "198.51.100.1", "username": "admin", "password": "admin"},
    "R2": {"hostname": "172.16.1.1", "username": "admin", "password": "admin"},
    "R3": {"hostname": "172.16.1.2", "username": "admin", "password": "admin"},
    "R4": {"hostname": "172.16.1.3", "username": "admin", "password": "admin"},
} ##defines the router_name= R1,R2,R3,R4; the hostname, username, password

def get_router_config(router_name, hostname, username, password): ##this functions takes the parameters from Router_crendentials
    driver = napalm.get_network_driver("ios")
    device = driver(hostname=hostname, username=username, password=password)

    try:
        device.open() #opens the connection
        running_config = device.get_config()["running"] # gets the running config when the connection is open
        device.close() #the connection is closed 
        return running_config.splitlines()  # Convert to list of lines for comparison
    except Exception as e:
        print(f"Error fetching config for {router_name}: {e}")
        return None

def get_latest_saved_config(router_name): # this function is used for taking the latest saved config from the directory
    files = [f for f in os.listdir(CONFIG_DIR) if f.startswith(f"Router ({router_name})")] #this line takes a list of files in 'CONFIG_DIR' that starts with Router ({router_name}). it uses a list comprehension and the os.listdir() function 

    if not files: #if no files are there this returns None
        return None

    latest_file = sorted(files, reverse=True)[0]  # this line sorts the list of files in reverse order so that we can get the latest file and take the first file [0].
    with open(os.path.join(CONFIG_DIR, latest_file), "r") as f: #this opens the latest file and reads it and return them as a list of lines.
        return f.read().splitlines()  

def compare_configs(router_name, new_config): # The newly fetched configuration as a list of lines
    old_config = get_latest_saved_config(router_name) #This retrieves the latest saved configuration for the router.

    if old_config is None: # If no old configuration is found, it returns a message indicating this.
        return [f"No previous config found for {router_name}.\n"]

    changes = [] #this initializes an empty list to store detected changes.

    for old, new in zip(old_config, new_config): #This compares each line of the old and new configs. If they're different, it adds both versions to the changes list.
        if old != new:
            changes.append(f"OLD CONFIG: {old}\nNEW CONFIG: {new}\n")

    for new in new_config: #This checks for lines in the new config that don't exist in the old config and adds them to change
        if new not in old_config:
            changes.append(f"NEW CONFIG: {new}\n")

    for old in old_config: #This checks for lines in the old config that don't exist in the new config and adds them to changes.
        if old not in new_config:
            changes.append(f"OLD CONFIG: {old}\n")

#This returns the list of changes if any were detected, or a message indicating no changes if the list is empty.
    return changes if changes else [f"No changes detected for {router_name}.\n"]

def main():
    results = {} #This initializes an empty dictionary to store results for each router.

    for router, creds in ROUTER_CREDENTIALS.items(): #This starts a loop that iterates over each router in the ROUTER_CREDENTIALS dictionary.
        new_config = get_router_config(router, creds["hostname"], creds["username"], creds["password"])
        if new_config:
            results[router] = compare_configs(router, new_config)
        else:
            results[router] = [f"Failed to fetch config for {router}"]

    return results #If a new configuration was successfully fetched, it compares it with the old configuration. If not, it adds an error message to the results.
