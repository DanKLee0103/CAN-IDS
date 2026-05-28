# Rolling window - how to implement logic just using timestamps?

# Check if the ID has exceeded a max count within the window for the new message that comes in
# If true, return string describing the alert. Otherwise, return None
# Implement a reset() method that clears all states
# name class attribute so the detector knows which rule was fired
from collections import defaultdict
from ..message import Message

class FloodingRule:
    name = "FloodingRule"

    def __init__(self, count:int):
        """
        Max count is the maximum amount of messages we should be seeing
        within the window that we set (which is 1 second for now)
        """
        self.max_count = count
        self.window_seconds = 1.0 # Can change this to be passed in later
        self.record = defaultdict(list)

    def check(self, message:Message):
        curr_record = self.record[message.id]
        curr_record.append(message.timestamp)
        for idx, time in enumerate(curr_record):
            # Keep looking until we reach a value within window range
            if time >= message.timestamp - self.window_seconds:
                self.record[message.id] = curr_record[idx:len(curr_record)]
                break
        # If we detect an issue, true, so return alarm detecting a problem. 
        # Otherwise, return None.
        if len(self.record[message.id]) > self.max_count:
            return f"Flood detected on ID 0x{message.id:03X}: {len(self.record[message.id])} messages in 1s"
        else:
            return None

    def reset(self):
        self.record = defaultdict(list)
