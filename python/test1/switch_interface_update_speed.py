import csv
from napalm import get_network_driver
from netmiko import ConnectHandler
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

INPUT_FILE = "switch_hosts.csv"
OUTPUT_FILE = "updated_interfaces.csv"

DEVICE_TYPE_MAPPING = {
    "cisco_ios": "ios",
    "juniper_junos": "junos"
}

def read_hosts(filename):
    hosts = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hosts.append(row)
    return hosts

def check_poe(net_connect, interface):
    """Check if interface has PoE enabled or device drawing power"""
    try:
        output = net_connect.send_command(f"show interface {interface} | include power|PoE")
        if "disabled" in output.lower() or "off" in output.lower():
            return False
        elif "PoE" in output or "power" in output.lower():
            return True
    except Exception as e:
        print(f"Error checking PoE on {interface}: {e}")
    return False

def update_speed(net_connect, interface):
    """Send config to update interface speed to 1Gbps"""
    commands = [
        f"interface {interface}",
        "speed 1000",
        "exit"
    ]
    net_connect.send_config_set(commands)

def get_filtered_interfaces(host):
    filtered = []
    driver_name = DEVICE_TYPE_MAPPING.get(host['device_type'])
    if not driver_name:
        print(f"Unsupported device type: {host['device_type']}")
        return filtered

    # Connect via NAPALM
    driver = get_network_driver(driver_name)
    device = driver(
        hostname=host['hostname'],
        username=host['username'],
        password=host['password']
    )

    try:
        device.open()
        interfaces = device.get_interfaces()

        # Use Netmiko for PoE + config changes
        net_connect = ConnectHandler(
            device_type="cisco_ios",
            host=host['hostname'],
            username=host['username'],
            password=host['password']
        )

        for intf, details in interfaces.items():
            speed = details.get('speed')
            if speed == 100:
                has_poe = check_poe(net_connect, intf)
                if has_poe:
                    print(Fore.RED + f"[{host['hostname']}] {intf} = 100Mbps + PoE detected, updating to 1Gbps")
                    update_speed(net_connect, intf)
                    filtered.append({
                        "hostname": host['hostname'],
                        "interface": intf,
                        "old_speed": speed,
                        "new_speed": 1000,
                        "poe_detected": has_poe,
                        "admin_status": details.get('is_up'),
                        "oper_status": details.get('is_up')
                    })
                else:
                    print(Fore.YELLOW + f"[{host['hostname']}] {intf} = 100Mbps but no PoE detected, skipping")
            elif speed == 1000:
                print(Fore.GREEN + f"[{host['hostname']}] {intf} = already 1Gbps, no change needed")

    except Exception as e:
        print(f"Error connecting to {host['hostname']}: {e}")
    finally:
        device.close()
        if 'net_connect' in locals():
            net_connect.disconnect()

    return filtered

def write_output(filtered_list, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ["hostname", "interface", "old_speed", "new_speed", "poe_detected", "admin_status", "oper_status"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in filtered_list:
            writer.writerow(entry)

def main():
    hosts = read_hosts(INPUT_FILE)
    all_filtered = []
    for host in hosts:
        filtered = get_filtered_interfaces(host)
        all_filtered.extend(filtered)

    write_output(all_filtered, OUTPUT_FILE)
    print(Fore.CYAN + f"\nUpdated interface report written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
