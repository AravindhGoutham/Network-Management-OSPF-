#!/usr/bin/env python3

import sqlite3
from prettytable import PrettyTable

# Connect to the database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Retrieve all data from the users table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Define table format using PrettyTable
table = PrettyTable()
table.field_names = [
    "ID", "Router IP", "Username", "Password", "Loopback IP", "Loopback Area",
    "OSPF Process ID", "Network Address 1", "Wildcard Mask 1", "Area 1",
    "Network Address 2", "Wildcard Mask 2", "Area 2"
]

# Add rows to the table
for row in rows:
    table.add_row(row)

# Print the table
print(table)

# Close database connection
conn.close()
