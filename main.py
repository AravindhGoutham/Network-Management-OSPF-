#!/usr/bin/env python3

from flask import Flask, render_template, request, send_from_directory
import sqlite3
import ospfconfig #importing ospfconfig program
import getconfig #importing getconfig program
import ping #importing ping program
import diffconfig #importing diffconfig program
import os 
from validateipv4 import validate_ipv4  # Importing validation function

app = Flask(__name__)

# Database setup 
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            router_ip TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            loopback_ip TEXT,
            loopback_area TEXT NOT NULL,
            ospf_process_id TEXT NOT NULL,
            network_address_1 TEXT,
            wildcard_mask_1 TEXT,
            area_1 TEXT NOT NULL,
            network_address_2 TEXT,
            wildcard_mask_2 TEXT,
            area_2 TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ospfconfig') #app route to ospfconfig it will go to the next page when ospfconfig is selected
def ospfconfig_page():
    return render_template("ospfconfig.html") #maps with the html file saved in templates

@app.route('/getconfig') #app route to getconfig it will go to the next page when getconfig is selected
def getconfig_page():
    files = getconfig.configurations()
    return render_template("getconfig.html", files=files) #maps with the html file saved in templates

@app.route('/pingtest') #app route to ping test it will go to the next page when ping is selected
def ping_test_page():
    results = ping.perform_ping_test()
    return render_template("pingtest.html", results=results) #maps with the html file saved in templates

@app.route('/diffconfig') #app route to diffconfig it will go to the next papge when it is selected
def diff_config_page():
    results = diffconfig.main()
    return render_template("diffconfig.html", results=results) #maps with the html file saved in templates

@app.route('/download/<filename>') #this is used to download the file from getconfig 
def download_file(filename):
    return send_from_directory(os.getcwd(), filename, as_attachment=True) #it saves the file in the current directory

@app.route('/submit', methods=['POST']) #this is used to get the user input for ospfconfig which will be seen when we select ospfconfig in the index page
def submit():
    if request.method == 'POST':
        router_ip = request.form.get('Router IP Address')
        username = request.form.get('Username')
        password = request.form.get('Password')
        ospf_process_id = request.form.get('OSPF Process ID')
        loopback_ip = request.form.get('Loopback IP', None) #optional
        loopback_area = request.form.get('Loopback Area', None) #optional
        network_address_1 = request.form.get('Network Address 1', None) #optional
        wildcard_mask_1 = request.form.get('Wildcard Mask 1', None) #optional
        area_1 = request.form.get('Area 1', None) #optional
        network_address_2 = request.form.get('Network Address 2', None) #optional
        wildcard_mask_2 = request.form.get('Wildcard Mask 2', None) #optional
        area_2 = request.form.get('Area 2', None) #optional

        # Validate all IP fields using validate_ipv4 from validateipv4.py
        for ip in [router_ip, loopback_ip, network_address_1, network_address_2,wildcard_mask_1,wildcard_mask_2]:
            if ip:
                validation_result = validate_ipv4(ip)
                if "Invalid" in validation_result:
                    return f"Error: {validation_result}", 400  # Return error if IP is invalid

        if not (router_ip and username and password and ospf_process_id): #these fields are mandatory if it is not given it will throw an error
            return "All mandatory fields are required!", 400

        try: #this is used to create a database which we enter in the ospfconfig.html 
            conn = sqlite3.connect("database.db") #name of the database
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (router_ip, username, password, loopback_ip, loopback_area, ospf_process_id, network_address_1, wildcard_mask_1, area_1, network_address_2, wildcard_mask_2, area_2) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (router_ip, username, password, loopback_ip, loopback_area, ospf_process_id, network_address_1, wildcard_mask_1, area_1, network_address_2, wildcard_mask_2, area_2))
            conn.commit()
        except sqlite3.Error as e:
            return f"Database error: {e}", 500
        finally:
            conn.close()

        ospfconfig.configure_ospf(router_ip) # when we enter the data in ospfconfig.html and press submit it will automatically configured ospf in the Router

        return f"Data uploaded and OSPF configured on {router_ip} successfully!" 

if __name__ == '__main__':
    app.run(debug=True,port=80)


