from typing import Dict, Optional, Tuple
from collections import defaultdict
from .loader import loader
import csv


# script written to extract valid ids for whitelist spoofing
with open("../otids_dataset/attack_free.csv", 'r') as file:
    reader = csv.DictReader(file)
    unique_ids = set()
    for row in reader:
        if row["ID1"] not in unique_ids:
            unique_ids.add(row["ID1"])
print(unique_ids)

# written to get max number an id shows up in 1-second window         
freq = defaultdict(int)

# Change the attack_free.csv to another dataset if want to see how many attacks in 1-second window
for msg, _ in loader("../otids_dataset/DoS_flood.csv"):
    freq[msg.id] += 1
max_normal = max(freq.values())
print(f"Max messages for any single ID in normal traffic: {max_normal}")

timestamps = defaultdict(list)
max_count = 0

for msg, _ in loader("../otids_dataset/attack_free.csv"):
    ts = msg.timestamp
    arb_id = msg.id
    window = [t for t in timestamps[arb_id] if t >= ts - 1.0]
    window.append(ts)
    timestamps[arb_id] = window
    if len(window) > max_count:
        max_count = len(window)

print(f"Max messages for any single ID in 1 second: {max_count}") # 124
