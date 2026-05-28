import pytest
from can_ids.message import Message
from can_ids.rules.spoofing import SpoofingRule


def msg(arb_id: int, ts: float) -> Message:
    return Message(id=arb_id, payload=b"\x00", timestamp=ts)

# Passing Case
def test_whitelist_known_id():
    """
    Send a known id in the whitelist but with timestamp difference 
    greater than 0.001
    """
    rule = SpoofingRule(whitelist=[0x123])
    assert rule.check(message=msg(arb_id=0x123, ts=1.0)) is None


# Error Case
def test_whitelist_unknown_id():
    """
    Send an unknown id in the whitelist with timestamp difference 
    greater than 0.001
    """
    rule = SpoofingRule(whitelist=[0x123])
    assert rule.check(message=msg(arb_id=0x129, ts=1.0)) == \
    "Spoof detected on ID 0x129: unrecognized ID"


# Passing Case
def test_dup_send_with_id_no_alert():
    """
    Send an id in the whitelist with timestamp difference > 0.001 seconds
    """
    rule = SpoofingRule(whitelist=[0x123])
    assert rule.check(message=msg(arb_id=0x123, ts=1.0)) is None


# Error Case
def test_dup_send_with_id_expect_alert():
    """
    Send an id in the whitelist with no timestamp difference
    """
    rule = SpoofingRule(whitelist=[0x123])
    assert rule.check(message=msg(arb_id=0x123, ts=0.0)) == \
    "Spoof detected on ID 0x123: multiple devices claiming same ID"

