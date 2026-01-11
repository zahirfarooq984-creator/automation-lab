#!/usr/bin/env python3

# ================================
# Check Point Malicious IP Blocker
# ================================
# This script demonstrates how to:
# - Login to Check Point Management API
# - Check if an IP object exists
# - Create it if not
# - Add it to a blocked IP group
# - Publish and install policy
# - Logout safely

import requests
import json
import sys
import urllib3

# Disable HTTPS warnings (lab only - do NOT do this in production)
urllib3.disable_warnings()

# ================================
# CONFIGURATION SECTION
# ================================

MGMT_SERVER = "https://192.168.1.100"   # Check Point Management IP
USERNAME = "api-admin"
PASSWORD = "SuperSecretPassword"
DOMAIN = "SMC User"

BLOCK_GROUP_NAME = "Malicious_IPs"      # Pre-created group in Check Point
POLICY_PACKAGE = "Standard"             # Policy package name

# The malicious IP we want to block
MALICIOUS_IP = "8.8.8.8"

# ================================
# HELPER FUNCTION TO CALL API
# ================================

def api_call(endpoint, payload, sid):
    """
    Generic function to call Check Point API endpoints
    """
    url = MGMT_SERVER + "/web_api/" + endpoint
    headers = {
        "Content-Type": "application/json"
    }

    if sid:
        headers["X-chkp-sid"] = sid

    response = requests.post(url, json=payload, headers=headers, verify=False)

    if response.status_code != 200:
        print(f"API call failed: {response.text}")
        sys.exit(1)

    return response.json()

# ================================
# 1. LOGIN
# ================================

print("[+] Logging into Check Point Management...")

login_payload = {
    "user": USERNAME,
    "password": PASSWORD,
    "domain": DOMAIN
}

login_response = api_call("login", login_payload, None)
SID = login_response["sid"]

print("[+] Login successful")

# ================================
# 2. CHECK IF IP OBJECT EXISTS
# ================================

print("[+] Checking if IP object exists...")

show_host_payload = {
    "name": MALICIOUS_IP
}

ip_exists = False

try:
    result = api_call("show-host", show_host_payload, SID)
    print("[+] IP object already exists")
    ip_exists = True
except:
    print("[+] IP object does not exist, will create it")

# ================================
# 3. CREATE IP OBJECT IF NEEDED
# ================================

if not ip_exists:
    print("[+] Creating IP object...")

    add_host_payload = {
        "name": MALICIOUS_IP,
        "ip-address": MALICIOUS_IP,
        "color": "red",
        "comments": "Automatically added malicious IP"
    }

    api_call("add-host", add_host_payload, SID)
    print("[+] IP object created")

# ================================
# 4. ADD IP TO BLOCK GROUP
# ================================

print("[+] Adding IP to Malicious IPs group...")

set_group_payload = {
    "name": BLOCK_GROUP_NAME,
    "members": {
        "add": [MALICIOUS_IP]
    }
}

api_call("set-group", set_group_payload, SID)

print("[+] IP added to block group")

# ================================
# 5. PUBLISH THE CHANGE
# ================================

print("[+] Publishing changes...")

api_call("publish", {}, SID)

print("[+] Changes published")

# ================================
# 6. INSTALL POLICY
# ================================

print("[+] Installing policy...")

install_payload = {
    "policy-package": POLICY_PACKAGE,
    "targets": ["All"]
}

api_call("install-policy", install_payload, SID)

print("[+] Policy installed")

# ================================
# 7. LOGOUT
# ================================

print("[+] Logging out...")

api_call("logout", {}, SID)

print("[+] Done. Malicious IP blocked successfully.")


