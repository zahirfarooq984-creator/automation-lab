# ping_test.py
import subprocess
from rich import print

# List of hosts to test
hosts = ["8.8.8.8", "192.168.1.1"]  # Replace with your lab IPs or hostnames

for host in hosts:
    try:
        # Run ping command
        result = subprocess.run(
            ["ping", "-c", "1", host],  # Use ["ping", "-n", "1", host] on Windows
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Check return code
        if result.returncode == 0:
            print(f"[green]{host} is UP[/green]")
        else:
            print(f"[red]{host} is DOWN[/red]")
    except Exception as e:
        print(f"[red]{host} check failed: {e}[/red]")


