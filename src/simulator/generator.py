"""
Simulates normal and attack CAN traffic for testing the detector.

Usage:
    gen = TrafficGenerator(seed=42) # 42 is conventional :)
    normal_msgs = gen.normal_traffic(n=100, start_time=0.0)
    flood_msgs  = gen.flood_attack(target_id=0x0C0, n=50, start_time=5.0)
"""

import random, time
from typing import List

from can_ids.message import Message


class TrafficGenerator:
    def __init__(self, seed: int = None):
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Normal traffic
    # ------------------------------------------------------------------

    def normal_traffic(
        self,
        n: int = 100,
        start_time: float = 0.0,
        ids: List[int] = None,
    ) -> List[Message]:
        """
        Generate n messages with realistic inter-message gaps (~10 ms).
        """
        if ids is None:
            ids = [0x0C0, 0x1A0, 0x200, 0x300, 0x400]

        messages = []
        ts = start_time
        for _ in range(n):
            arb_id = self._rng.choice(ids)
            payload = bytes(self._rng.randint(0, 255) for _ in range(8))
            messages.append(Message(id=arb_id, payload=payload, timestamp=ts))
            ts += self._rng.uniform(0.008, 0.012)  # 8–12 ms gap (arbitrary gap)
        return messages

    # ------------------------------------------------------------------
    # Attack scenarios
    # ------------------------------------------------------------------

    def flood_attack(
        self,
        n: int,
        target_id: int,
        start_time: float = 0.0
    ) -> List[Message]:
        """
        Flood attack generator. 

        Every 0.00001 seconds, a new message with the same target id and random payload (data) is sent.
        This saturates the bus bandwidth, leading to a system error, allowing for data exposure.
        """

        messages = []
        ts = start_time

        # Every 0.00001 seconds, append new message with target id, random data, and timestamp
        for _ in range(n):
            payload = bytes(self._rng.randint(0, 255) for _ in range(8))
            messages.append(Message(id=target_id, payload=payload, timestamp=ts))
            ts += 0.00001
        return messages


    def spoof_attack(
        self,
        n: int,
        target_id: int,
        start_time: float = 0.0,
        attack_type: str = 'unknown_id'
    ) -> List[Message]:
        """
        Spoof attack generator. 

        Two types of attacks - unknown ID attack & duplicate sender attack

        unknown ID attack: message containing ID that is undefined in the preset list of valid IDs
        duplicate ID attack: two devices claiming the same ID (time gap too short between each tx)
        """

        messages = []
        ts = start_time

        if attack_type == 'unknown_id':
            for _ in range(n):
                payload = bytes(self._rng.randint(0, 255) for _ in range(8))
                messages.append(Message(id=target_id, payload=payload, timestamp=ts))
            
        elif attack_type == 'duplicate_send':
            for _ in range(n):
                payload = bytes(self._rng.randint(0, 255) for _ in range(8))
                messages.append(Message(id=target_id, payload=payload, timestamp=ts))
                ts += 0.0005 # timestamp boundary for SpoofingRule is currently 0.001 so anything less than that
        return messages


    def payload_attack(
        self,
        n: int,
        target_id: int,
        start_time: float = 0.0,
    ) -> List[Message]:
        """
        Payload attack generator. 

        The payload value for a preset spec ID in the message does not fit within the spec range.

        For example, if ID corresponds to vehicle speed and if the value is not within
        the pre-defined range for speed, this defines a payload attack.
        """

        messages = []
        ts = start_time

        DEFAULT_SPEC_IDS = [0x0C0, 0x1A0]

        for _ in range(n):
            for spec_id in DEFAULT_SPEC_IDS:
                # Payload set to maxint for simplicity
                payload = (65535).to_bytes(2, byteorder='big') + bytes(6)
                messages.append(Message(id=spec_id, payload=payload, timestamp=ts))
                ts += 0.1
        
        return messages
