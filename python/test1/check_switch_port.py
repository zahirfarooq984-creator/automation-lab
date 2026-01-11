#!/usr/bin/env python3

import csv
from netmiko import ConnectHandler
from openpyxl import Workbook

# ================================================
# CONFIGURATION
# ================================================
csv_file = "switch_list.csv"  # CSV containing switches with columns: hostname, username, password, device_type
output_excel = "switch_ports_report.xlsx"

# ================================================
# FUNCTION TO READ SWITCHES FROM CSV
# ================================================
def read_switches(csv_file):
    switches = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            switches.append(row)
    return switches

# ================================================
# FUNCTION TO CONNECT TO SWITCH AND CHECK INTERFACES
# ================================================
def check_interfaces(switch):
    # Results list
    results = []

    # Connect to switch using Netmiko
    try:
        connection = ConnectHandler(
            host=switch['hostname'],
            username=switch['username'],
            password=switch['password'],
            device_type=switch['device_type']
        )

        # Get interface status
        # 'show running-config' for speed config
        output = connection.send_command("show running-config | include speed")
        # 'show interface status' to see IP phones connected and operational status
        interface_output = connection.send_command("show interface status")

        # Split lines for processing
        lines = interface_output.splitlines()

        for line in lines[1:]:  # skip header
            parts = line.split()
            if len(parts) < 4:
                continue  # Skip incomplete lines
            intf = parts[0]
            status = parts[1]
            vlan = parts[2]
            duplex = parts[3]

            # Check for manually configured speed 100
            if f"{intf} speed 100" in output:
                # Check if PoE is being used (IP phone likely attached)
                poe_output = connection.send_command(f"show running-config interface {intf} | include power inline")
                if "power inline" in poe_output.lower():
                    # If both conditions met, add to results
                    results.append({
                        "Switch": switch['hostname'],
                        "Interface": intf,
                        "Current Speed": "100 Mbps",
                        "Recommended Speed": "1 Gbps"
                    })

                    # ==================================================
                    # If this were an actual change script, you could
                    # send a config change here to set speed to 1G
                    # connection.send_config_set([f"interface {intf}", "speed 1000"])
                    # ==================================================

        connection.disconnect()

    except Exception as e:
        # If switch connection fails, log it
        results.append({
            "Switch": switch['hostname'],
            "Interface": "N/A",
            "Current Speed": "ERROR",
            "Recommended Speed": f"Connection failed: {str(e)}"
        })

    return results

# ================================================
# MAIN SCRIPT
# ================================================
def main():
    switches = read_switches(csv_file)

    all_results = []

    for sw in switches:
        sw_results = check_interfaces(sw)
        all_results.extend(sw_results)

    # ================================================
    # WRITE RESULTS TO EXCEL
    # ================================================
    wb = Workbook()
    ws = wb.active
    ws.title = "Switch Port Report"

    # Write headers
    ws.append(["Switch", "Interface", "Current Speed", "Recommended Speed"])

    # Write rows
    for row in all_results:
        ws.append([row["Switch"], row["Interface"], row["Current Speed"], row["Recommended Speed"]])

    # Save Excel file
    wb.save(output_excel)
    print(f"Report saved to {output_excel}")

# ================================================
# RUN SCRIPT
# ================================================
if __name__ == "__main__":
    main()


