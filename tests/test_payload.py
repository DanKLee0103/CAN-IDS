import pytest
from can_ids.message import Message
from can_ids.rules.payload import PayloadRule


def msg(arb_id: int, data: bytes) -> Message:
    return Message(id=arb_id, payload=data, timestamp=0.0)


def test_valid_rpm_speed_no_alert():
    """
    Checks to see that RPM and speed don't alert if detected properly
    """
    rule = PayloadRule()
    # RPM = 3000 (0x0BB8), within [0, 8000]
    # Speed = 11 (0x0B), within [0, 200]
    assert rule.check(msg(arb_id=0x0C0, data=b"\x0b\xb8\x00\x00\x00\x00\x00\x00")) is None
    assert rule.check(msg(arb_id=0x1A0, data=b"\x00\x00\x0b\x00\x00\x00\x00\x00")) is None


def test_rpm_out_of_range_flagged():
    """
    Checks out of range for RPM
    """
    rule = PayloadRule()
    # RPM = 65535 — way above 8000
    alert = rule.check(msg(0x0C0, b"\xff\xff\x00\x00\x00\x00\x00\x00"))
    assert alert is not None


def test_speed_out_of_range_flagged():
    """
    Checks out of range for speed
    """
    rule = PayloadRule()
    # Speed = 255 — above 200
    alert = rule.check(msg(0x1A0, b"\x00\x00\xff\x00\x00\x00\x00\x00"))
    assert alert is not None


def test_payload_too_short_flagged():
    """
    Checks to see if specs have valid payload length
    """
    rule = PayloadRule()
    rpm_alert = rule.check(msg(0x0C0, b"")) # needs at least 2 bytes for RPM
    speed_alert = rule.check(msg(0x1A0, b"")) # needs at least 1 byte for Speed
    assert rpm_alert is not None 
    assert speed_alert is not None


def test_unknown_id_skipped():
    """
    Checks to see that unknown id are skipped as payload detection cannot detect
    """
    rule = PayloadRule()
    # ID not in spec — should pass through silently.
    # This is a robust case (checking although not entirely relevant).
    # Test cases like this can help with debugging.
    assert rule.check(msg(0x7ff, b"\xff\xff\xff\xff")) is None
