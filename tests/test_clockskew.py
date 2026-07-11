import pytest
from can_ids.message import Message
from can_ids.rules.clockskew import ClockskewRule

def test_no_drift_diff():
    """
    No drift diff. Slope is same as baseline slope.
    """

    rule = ClockskewRule(mean_intervals={0x1ac: 0.01}, slopes={0x1ac: 0.0})
    for i in range(200):
        message = Message(id=0x1ac, payload=bytes([123]), timestamp=i * 0.01)
        result = rule.check(message)
    assert result is None


def test_drift_detected():
    """
    Same setup as no drift but timestamps have growing drift (i * 0.01 + i * 5e-4), 
    assert result is not None
    """

    rule = ClockskewRule(mean_intervals={0x1ac: 0.01}, slopes={0x1ac: 0.0})
    for i in range(200):
        message = Message(id=0x1ac, payload=bytes([123]), timestamp=i * 0.01 + i * 5e-4)
        result = rule.check(message)
    assert result is not None


def test_insufficient_messages():
    """
    Only send 29 messages, assert result is None (early return)
    """

    rule = ClockskewRule(mean_intervals={0x1ac: 0.01}, slopes={0x1ac: 0.0})
    for i in range(29):
        message = Message(id=0x1ac, payload=bytes([123]), timestamp=i * 0.01 + i * 5e-4)
        result = rule.check(message)
    assert result is None


def test_unknown_id():
    """
    send 200 messages for ID 0x1ac 
    but initialize the rule with slopes for a different ID (0x123), 
    assert result is None
    """

    rule = ClockskewRule(mean_intervals={0x1ac: 0.01}, slopes={0x1ac: 0.0})
    for i in range(200):
        message = Message(id=0x123, payload=bytes([123]), timestamp=i * 0.01 + i * 5e-4)
        result = rule.check(message)
    assert result is None
