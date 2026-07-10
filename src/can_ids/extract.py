from collections import defaultdict
from .loader import loader
from typing import Dict, Optional, Tuple

import csv
import numpy as np
import statistics

if __name__ == "__main__":
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

# function to get clock skew mean interval for each ECU
def get_mean_intervals(filepath: str) -> dict:
    gaps = defaultdict(list) # id -> list of gaps
    prev_timestamps = {} # id -> last seen timestamp

    for msg, _ in loader(filepath):
        if msg.id in prev_timestamps:
            gap = msg.timestamp - prev_timestamps[msg.id]
            gaps[msg.id].append(gap)
        prev_timestamps[msg.id] = msg.timestamp

    mean_intervals = {id: statistics.mean(g) for id, g in gaps.items()}
    return mean_intervals

# function to get slope for clock skew drift rate
def get_baseline_slopes(filepath: str, mean_intervals: dict) -> dict:
    # collect all timestamps per id
    timestamps = defaultdict(list)
    for msg, _ in loader(filepath):
        timestamps[msg.id].append(msg.timestamp)

    slopes = {}
    for arb_id, ts_list in timestamps.items():
        if len(ts_list) < 30: # need enough points -- set to 30 for now
            continue
        first = ts_list[0]
        mean_iv = mean_intervals[arb_id]
        errors = [ts_list[i] - (first + i * mean_iv) for i in range(len(ts_list))]  # list of (actual - expected) for each message
        slope, _ = np.polyfit(range(len(errors)), errors, 1)
        slopes[arb_id] = slope

    return slopes
