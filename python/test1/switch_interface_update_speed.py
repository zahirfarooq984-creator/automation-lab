from netmiko import ConnectHandler
import pandas as pd
import csv

REPORT = []

def check_and_fix_switch(device):
    print(f"Connecting to {device['hostname']}")

    try:
        conn = ConnectHandler(**device)
    except Exception as e:
        print(f"Failed to connect to {device['hostname']}: {e}")
        return

    # Get interface status
    output = conn.send_command("show interfaces status")

    lines = output.splitlines()[1:]

    for line in lines:
        parts = line.split()
        if len(parts) < 6:
            continue

        interface = parts[0]
        speed = parts[-2]

        old_speed = speed
        new_speed = speed
        action = "Skipped"
        reason = "Not 100M"

        # Only interested in hardcoded 100Mb
        if speed == "100":
            poe = conn.send_command(f"show power inline {interface}")

            if "Power" in poe or "on" in poe.lower():
                reason = "Phone detected"
                print(f"{device['hostname']} {interface} has phone and is 100Mb -> upgrading")

                commands = [
                    f"interface {interface}",
                    "speed 1000",
                    "end"
                ]

                conn.send_config_set(commands)
                new_speed = "1000"
                action = "CHANGED"

            else:
                reason = "No phone detected"

        REPORT.append({
            "Switch": device["hostname"],
            "Interface": interface,
            "Old Speed": old_speed,
            "New Speed": new_speed,
            "Action": action,
            "Reason": reason
        })

    conn.disconnect()

# Load switches
devices = []

with open("switches.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        devices.append({
            "device_type": row["device_type"],
            "host": row["ip"],
            "username": row["username"],
            "password": row["password"],
            "hostname": row["hostname"]
        })

# Run against all switches
for device in devices:
    check_and_fix_switch(device)

# Write Excel report
df = pd.DataFrame(REPORT)
df.to_excel("switch_port_speed_audit.xlsx", index=False)

print("\n✅ Report written to switch_port_speed_audit.xlsx")
