from collections import defaultdict, deque
from ..message import Message
import numpy as np

class ClockskewRule:
    name = "ClockskewRule"

    def __init__(self, mean_intervals: dict, slopes: dict):
        self.first_timestamps = {} # arb_id -> very first timestamp ever seen
        self.timestamps = defaultdict(lambda: deque(maxlen=200)) # arb_id -> deque of (global_index, timestamp)
        self.msg_counts = defaultdict(int) # arb_id -> cumulative count (never resets)
        self.mean_intervals = mean_intervals
        self.baseline_slopes = slopes
        self.error_range = 10**(-4)

    def check(self, message:Message):
        if message.id not in self.first_timestamps:
            self.first_timestamps[message.id] = message.timestamp

        self.msg_counts[message.id] += 1
        self.timestamps[message.id].append([self.msg_counts[message.id], message.timestamp])
        
        # early return if < 30 or ID not in baseline
        if len(self.timestamps[message.id]) < 30 or message.id not in self.baseline_slopes:
            return None


        indices, ts_vals = zip(*self.timestamps[message.id])
        first = self.first_timestamps[message.id]
        mean_iv = self.mean_intervals[message.id]
        errors = [ts_vals[i] - (first + indices[i] * mean_iv) for i in range(len(indices))]
        live_slope, _ = np.polyfit(indices, errors, 1)
        diff = abs(live_slope - self.baseline_slopes[message.id])
        if diff > self.error_range:
            return (f"Clockskew difference detected on ID 0x{message.id:03X}: "
                    f"drift diff={diff:.2e} (expected={self.baseline_slopes[message.id]:.2e}, actual={live_slope:.2e})")
        return None

    def reset(self):
        self.timestamps = defaultdict(lambda: deque(maxlen=200))
        self.first_timestamps = {}
        self.msg_counts = defaultdict(int)
