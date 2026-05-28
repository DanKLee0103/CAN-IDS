from typing import Dict, Optional, Tuple
import csv
from .message import Message

def loader(filepath: str):
    """
    Loads OTIDS dataset into IDS
    """
    messages = []

    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert timestamp and id
            ts = float(row["TS"])
            id = int(row["ID1"], 16)
            # ID0 ignored

            payload = bytearray()
            # dlc for payload
            for dlc in [row["DLC0"],row["DLC1"],row["DLC2"],row["DLC3"],
                        row["DLC4"],row["DLC5"],row["DLC6"],row["DLC7"]]:
                # if empty value, load 0
                if dlc == '':
                    payload.append(0)
                else:
                    payload.append(int(dlc, 16))
            payload = bytes(payload)
            messages.append((Message(id=id, payload=payload, timestamp=ts), int(row["target"])))
    return messages
