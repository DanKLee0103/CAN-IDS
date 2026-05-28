from typing import Dict, List, Optional, Set
from collections import defaultdict

from ..message import Message

class SpoofingRule:
    name = "SpoofingRule"

    def __init__(self, whitelist: List[int]):
        self.whitelist_set = set(whitelist)
        self.whitelist = {id: 0 for id in whitelist}
        self.timestamp_boundary = 0.001

    # For the spoofing rule, check if this next message is either:
    # - Unrecognized ID (ID not in whitelist)
    # - Invalid timeframe (the same ID shows up within 0.001 seconds)
    def check(self, message:Message):
        if message.id not in self.whitelist_set:
            return f"Spoof detected on ID 0x{message.id:03X}: unrecognized ID"
        if message.timestamp - self.whitelist[message.id] <= self.timestamp_boundary:
            self.whitelist[message.id] = message.timestamp # Update last seen timestamp for ID
            return f"Spoof detected on ID 0x{message.id:03X}: multiple devices claiming same ID"
        self.whitelist[message.id] = message.timestamp # Update last seen timestamp for ID
        return None # Otherwise, return None

    def reset(self):
        self.whitelist = {id: 0 for id in self.whitelist_set}
