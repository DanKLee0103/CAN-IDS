from typing import Dict, Optional, Tuple

from ..message import Message

DEFAULT_SPEC = {
    # Format: (start_byte, end_byte, (min_val, max_val))
    0x0C0: (0, 2, (0, 8000)), # RPM
    0x1A0: (2, 3, (0, 200))   # Speed
}

class PayloadRule:
    name = "PayloadRule"

    def __init__(self, custom_spec=None):
        if custom_spec is not None:
            self.spec = custom_spec
        else:
            self.spec = DEFAULT_SPEC
        
    def check(self, message):
        if message.id in self.spec:
            byte_begin, byte_end, valid_range = self.spec[message.id]
            min_range, max_range = valid_range
            if len(message.payload) < byte_end - byte_begin:
                return f"Payload intrusion detected on ID 0x{message.id:03X}: payload needs to be at least {byte_end - byte_begin} bytes"

            curr_val = int.from_bytes(message.payload[byte_begin:byte_end], byteorder="big")
            if curr_val < min_range:
                return f"Payload intrusion detected on ID 0x{message.id:03X}: current value less than minimum value for spec"
            elif curr_val > max_range:
                return f"Payload intrusion detected on ID 0x{message.id:03X}: current value greater than maximum value for spec" 
        return None

    def reset(self):
        self.spec = DEFAULT_SPEC
