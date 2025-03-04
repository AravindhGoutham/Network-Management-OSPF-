#!/usr/bin/env python3

import sqlite3
from napalm import get_network_driver

def configure_ospf(router_ip):
    # Connect to the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Fetch only the specific router details based on router_ip
    cursor.execute("SELECT username, password, ospf_process_id, loopback_ip, loopback_area, network_address_1, wildcard_mask_1, area_1, network_address_2, wildcard_mask_2, area_2 FROM users WHERE router_ip = ?", (router_ip,))
    router = cursor.fetchone()
    conn.close()

    # Check if router exists in the database
    if not router:
        print(f"No router found with IP {router_ip}")
        return f"Router {router_ip} not found in the database."

    # Unpack router details
    username, password, ospf_process_id, loopback_ip, loopback_area, network_address_1, wildcard_mask_1, area_1, network_address_2, wildcard_mask_2, area_2 = router

    print(f"\n Configuring OSPF on Router: {router_ip}")

    # Initialize Napalm driver for IOS devices
    driver = get_network_driver("ios") 
    device = driver(hostname=router_ip, username=username, password=password)

    try:
        device.open()  # Establish SSH connection

        # Start OSPF configuration commands
        config_commands = f"""
        router ospf {ospf_process_id}
        """

        # Add loopback IP to OSPF configuration if available
        if loopback_ip:
            config_commands += f"\n network {loopback_ip} 0.0.0.0 area {loopback_area}"

        # Add first network to OSPF configuration if available
        if network_address_1 and wildcard_mask_1:
            config_commands += f"\n network {network_address_1} {wildcard_mask_1} area {area_1}"

        # Add second network to OSPF configuration if available
        if network_address_2 and wildcard_mask_2:
            config_commands += f"\n network {network_address_2} {wildcard_mask_2} area {area_2}"

        config_commands += "\n exit"

        # Apply configuration to the device
        device.load_merge_candidate(config=config_commands)
        device.commit_config()
        device.close()

        print(f"Successfully configured OSPF on {router_ip}")
        return f"OSPF configured successfully on {router_ip}"

    except Exception as e:
        print(f"Failed to configure {router_ip}: {str(e)}")
        return f"Failed to configure {router_ip}: {str(e)}"
