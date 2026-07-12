"""
generate_dataset.py
--------------------
One-time helper script used to build dataset/incidents.csv.
This is NOT part of the running Flask app — it's just used once
to populate realistic sample data. You can re-run it any time to
regenerate a fresh dataset.

Run with: python generate_dataset.py
"""

import random
import csv
from datetime import datetime, timedelta

random.seed(42)

ATTACK_TYPES = [
    "Phishing", "Malware", "Trojan", "Worm", "Spyware", "Ransomware",
    "SQL Injection", "Cross Site Scripting", "DDoS", "Brute Force",
    "Insider Threat", "Credential Stuffing", "DNS Spoofing", "Zero-Day Attack"
]

SEVERITIES = ["Low", "Medium", "High", "Critical"]

DEST_SYSTEMS = [
    "Mail Server", "Web Server", "Database Server", "File Server",
    "Domain Controller", "HR Portal", "Finance System", "VPN Gateway",
    "Employee Workstation", "Cloud Storage Bucket", "Customer Database",
    "Payment Gateway", "Internal Wiki", "CRM System"
]

DETECTION_TOOLS = [
    "SIEM (Splunk)", "CrowdStrike Falcon", "Snort IDS", "Microsoft Defender",
    "Wireshark", "Nessus Scanner", "IBM QRadar", "Palo Alto Firewall Logs",
    "Fail2Ban", "AWS GuardDuty"
]

MALWARE_NAMES = [
    "Trojan.GenKD", "Emotet", "TrickBot", "WannaCry", "Ryuk",
    "AgentTesla", "Zeus", "Locky", "NotPetya", "REvil", "Qbot", "N/A"
]

STATUSES = ["Open", "Investigating", "Contained", "Resolved", "Closed"]

ACTIONS = [
    "Blocked Source IP", "Isolated Affected Host", "Disabled User Account",
    "Reset User Credentials", "Applied Security Patch", "Restored from Backup",
    "Escalated to Incident Response Team", "Deployed Firewall Rule",
    "Ran Full Antivirus Scan", "Notified Affected Users", "Revoked Access Tokens",
    "Blocked Malicious Domain"
]

FIRST_NAMES = ["Alice", "Raj", "Maria", "John", "Priya", "David", "Fatima", "Wei",
               "Carlos", "Emma", "Liam", "Sofia", "Noah", "Aisha", "Tom"]
LAST_NAMES = ["Johnson", "Kumar", "Garcia", "Smith", "Sharma", "Lee", "Khan",
              "Chen", "Diaz", "Brown", "Miller", "Rossi", "Nguyen", "Patel", "Wilson"]


def random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def random_date():
    start = datetime(2025, 1, 1)
    end = datetime(2026, 6, 30)
    delta = end - start
    random_days = random.randint(0, delta.days)
    dt = start + timedelta(days=random_days)
    return dt.strftime("%Y-%m-%d")


def random_time():
    return f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"


def random_user():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def severity_for_attack(attack):
    # Weight severities realistically per attack type
    if attack in ["Ransomware", "Zero-Day Attack", "DDoS"]:
        return random.choices(SEVERITIES, weights=[5, 15, 40, 40])[0]
    if attack in ["Phishing", "Brute Force", "Credential Stuffing"]:
        return random.choices(SEVERITIES, weights=[30, 40, 25, 5])[0]
    return random.choices(SEVERITIES, weights=[20, 35, 30, 15])[0]


def generate_row(incident_id):
    attack = random.choice(ATTACK_TYPES)
    severity = severity_for_attack(attack)
    malware = random.choice(MALWARE_NAMES) if attack in ["Malware", "Trojan", "Worm", "Spyware", "Ransomware"] else "N/A"

    return {
        "incident_id": f"INC-{incident_id:04d}",
        "date": random_date(),
        "time": random_time(),
        "attack_type": attack,
        "severity": severity,
        "source_ip": random_ip(),
        "destination_system": random.choice(DEST_SYSTEMS),
        "affected_user": random_user(),
        "malware": malware,
        "detection_tool": random.choice(DETECTION_TOOLS),
        "status": random.choice(STATUSES),
        "action_taken": random.choice(ACTIONS),
    }


def main():
    rows = [generate_row(i) for i in range(1001, 1001 + 120)]
    fieldnames = list(rows[0].keys())

    with open("dataset/incidents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} incidents into dataset/incidents.csv")


if __name__ == "__main__":
    main()
