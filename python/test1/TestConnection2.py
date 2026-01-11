# network_status_check.py

from netmiko import ConnectHandler
from napalm import get_network_driver
from rich import print
from rich.table import Table
import subprocess
import pandas as pd

# --- List of devices to check ---
devices = [
    {
        "name": "Firewall1",
        "host": "192.168.1.10",
        "device_type": "cisco_ios",  # Netmiko type
        "username": "admin",
        "password": "password",
        "vendor": "cisco"  # For NAPALM
    },
    {
        "name": "Firewall2",
        "host": "192.168.1.20",
        "device_type": "cisco_ios",
        "username": "admin",
        "password": "password",
        "vendor": "cisco"
    }
]

results = []

for dev in devices:
    device_name = dev["name"]
    ip = dev["host"]

    # --- 1. Ping test using subprocess ---
    try:
        ping_result = subprocess.run(
            ["ping", "-c", "1", ip], capture_output=True
        )
        ping_status = "UP" if ping_result.returncode == 0 else "DOWN"
    except Exception as e:
        ping_status = f"ERROR ({e})"

    # --- 2. Netmiko interface check ---
    try:
        net_conn = ConnectHandler(
            device_type=dev["device_type"],
            host=ip,
            username=dev["username"],
            password=dev["password"]
        )
        net_output = net_conn.send_command("show ip interface brief")
        net_conn.disconnect()
        # simple parsing: mark interfaces as UP/DOWN
        interfaces = []
        for line in net_output.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 6:
                intf, status, proto = parts[0], parts[4], parts[5]
                intf_status = "UP" if status.lower() == "up" and proto.lower() == "up" else "DOWN"
                interfaces.append((intf, intf_status))
    except Exception as e:
        interfaces = [(f"ERROR ({e})", "N/A")]

    # --- 3. NAPALM interface check ---
    try:
        driver = get_network_driver(dev["vendor"])
        napalm_dev = driver(ip, dev["username"], dev["password"])
        napalm_dev.open()
        napalm_interfaces = napalm_dev.get_interfaces()
        napalm_dev.close()
    except Exception as e:
        napalm_interfaces = {f"ERROR ({e})": "N/A"}

    # --- Save result for report ---
    results.append({
        "Device": device_name,
        "Ping": ping_status,
        "Netmiko_Interfaces": interfaces,
        "NAPALM_Interfaces": napalm_interfaces
    })

# --- 4. Display results in a Rich table ---
table = Table(title="Network Device Status")

table.add_column("Device", style="cyan")
table.add_column("Ping", style="magenta")
table.add_column("Netmiko Interfaces", style="green")
table.add_column("NAPALM Interfaces", style="yellow")

for r in results:
    nm_intf_str = "\n".join([f"{i[0]}: {i[1]}" for i in r["Netmiko_Interfaces"]])
    nap_intf_str = "\n".join([f"{k}: {v['is_up']}" for k, v in r["NAPALM_Interfaces"].items() if isinstance(v, dict)])
    table.add_row(r["Device"], r["Ping"], nm_intf_str, nap_intf_str)

print(table)

# --- 5. Save results to Excel via pandas ---
df = pd.DataFrame(results)
df.to_excel("network_status_report.xlsx", index=False)
print("[bold green]Report saved to network_status_report.xlsx[/bold green]")
