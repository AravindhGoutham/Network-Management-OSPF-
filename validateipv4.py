#!/usr/bin/env python3

import json
import ipaddress

def validate_ipv4(ip):

    try:
        ip_obj = ipaddress.IPv4Address(ip)

        if ip_obj.is_multicast:
            return f"Invalid {ip} - it is a multicast address"
        if ip_obj.is_loopback:
            return f"Invalid {ip} - it is a loopback address"
        if ip_obj.is_link_local:
            return f"Invalid {ip} - it is a link-local address"
        if ip_obj.is_reserved:
            return f"Invalid {ip} - it is a reserved address"
        if ip_obj == ipaddress.IPv4Address("255.255.255.255"):
            return f"Invalid {ip} - it is a broadcast address"

        return f"Valid {ip}"

    except ipaddress.AddressValueError:
        return f"Invalid {ip} - it is not a valid IPv4 address"

def get_ssh_info(json_info):

    try:
        with open(json_info, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error")
        return None

def main():
    json_info="SSHinfo.json"
    # Get SSH info from JSON file
    ssh_data = get_ssh_info(json_info)
    if not ssh_data:
        print("Error")
        return

    # Validate IP addresses
    print("IP Address Validation Results:")
    for device in ssh_data:
        ip = device.get("IP")
        hostname = device.get("hostname")
        if ip:
            result = validate_ipv4(ip)
            print(f"{hostname} - {result}")
        else:
            print(f"{hostname} - No IP address found.")

if __name__ == "__main__":
    main()
