class Message:
    # Represent a single CAN message (CAN ID, payload, timestamp, extended flag)
    # - CAN ID (int)
    # - Payload (bytes, MAX 8 bytes)
    # - Timestamp (float)
    # - If extended ID, then a flag at the end to represent it

    def __init__(self, id: int, payload:bytes, timestamp:float, extended_flag:bool=False):
        self.id = id
        self.payload = payload
        self.timestamp = timestamp
        self.extended_flag = extended_flag

        max_id_bound = 0x1FFFFFFF if extended_flag else 0x7FF
        if id < 0 or id > max_id_bound or len(payload) > 8:
            raise ValueError
    
    def __repr__(self):
        return f"Message(id=0x{self.id:03X}, payload={self.payload!r}, \
        timestamp={self.timestamp!r}, extended_flag={self.extended_flag!r})"
