from typing import Dict, Optional, Tuple

from can_ids.loader import loader
from can_ids.detector import Detector
import csv

import time
start = time.time() # for throughput

#---------------------------------------------------------------
# This is the core file that evaluates the functionality
# and accuracy of the IDS given a dataset with proven benchmark. 
# Given the accuracy and performance, optimizations
# will be made accordingly.
#---------------------------------------------------------------

filepaths = [
    "otids_dataset/attack_free.csv", # target == 0
    "otids_dataset/DoS_flood.csv", # target == 1
    "otids_dataset/Fuzzy_spoof_payload.csv", # target == 2
    "otids_dataset/Impersonation_spoof.csv"  # target == 3
]

# true_positives — detector fired an alert AND target > 0 (correctly caught an attack)
# false_negatives — detector fired no alert AND target > 0 (missed an attack)
# false_positives — detector fired an alert AND target == 0 (wrongly flagged normal traffic)
# true_negatives — detector fired no alert AND target == 0 (correctly ignored normal traffic)
true_positives = 0
false_negatives = 0
false_positives = 0
true_negatives = 0

valid_ids = [int(x, 16) for x in \
            ['04f2', '0545', '0164', '04b1', '0153', '02a0', '0382', \
             '0018', '0510', '0587', '05e4', '0044', '0316', '0220', \
             '05a2', '05f0', '00a1', '0690', '0260', '04f0', '0034', \
             '02c0', '01f1', '0081', '05a0', '0043', '051a', '018f', \
             '04b0', '0080', '0042', '02b0', '04f1', '0350', '043f', \
             '0120', '0165', '00a0', '0050', '059b', '0370', '0110', \
             '0517', '0440', '0329'] \
            ]

detector = Detector(count=125, whitelist=valid_ids)
with open("otids_dataset/Impersonation_spoof.csv") as f:
    first_row = next(csv.DictReader(f))
    impersonation_start = float(first_row["TS"])

# for loop for all filepaths  
for path in filepaths:
    messages = loader(filepath=path)
    total_msgs = len(messages)

    for msg, target in messages:
        # According to the dataset
        # Impersonation Attack: 0-250 sec is attack-free, 
        # after 250 sec is under attack. But all rows are labeled target=3.
        if path == "otids_dataset/Impersonation_spoof.csv" and msg.timestamp < impersonation_start + 250:
            continue  # skip the attack-free period
            
        alert_len = len(detector.process(msg))

        # if alert, the detector.process should return a list of alert(s) that is not empty
        if alert_len > 0:
            # if message target is 0, wrongly flagged normal traffic
            if target == 0:
                false_positives += 1
            elif target > 0:
                true_positives += 1
            # Target value negative? Should never reach this.
            else:
                raise ValueError
        else: # alert_len == 0, so no alerts
            if target == 0:
                true_negatives += 1
            elif target > 0:
                false_negatives += 1

# Detection rate = true_positives / (true_positives + false_negatives)
# False positive rate = false_positives / (false_positives + true_negatives)
detection_rate = true_positives / (true_positives + false_negatives)
false_positive_rate = false_positives / (false_positives + true_negatives)

print(f"Detection rate: {detection_rate * 100:.2f}%")
print(f"False positive rate (wrongly detected error on normal traffic): {false_positive_rate * 100:.2f}%")

# Throughput measurement
elapsed = time.time() - start
total_msgs = true_positives + false_negatives + false_positives + true_negatives
print(f"Processed {total_msgs} messages in {elapsed:.2f}s ({total_msgs/elapsed:.0f} msgs/sec)")
