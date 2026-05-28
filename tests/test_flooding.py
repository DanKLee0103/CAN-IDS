import pytest
from can_ids.message import Message
from can_ids.rules.flooding import FloodingRule

# Macros
max_count = 5

def flood_id(rule, id):
    """
    Floods a single id using FloodingRule (passed in)
    """
    timestamp = 0.0
    for i in range(max_count+1): # Exceed max count by 1
        message = Message(id=id, payload=bytes([123]), timestamp=timestamp) # Use same id
        if i == max_count: 
            assert rule.check(message) is not None # TODO: change this to check for exact message later
        else:
            assert rule.check(message) is None
        timestamp += 0.1 # Increment timestamp


def test_valid_msg_no_alert():
    """
    Check that no alert is displayed with normal traffic
    """
    rule = FloodingRule(count=max_count)
    message = Message(id=0x1ac, payload=bytes([123]), timestamp=0.0) # id, payload, timestamp, extended_flag (omitted for this case)
    assert rule.check(message) is None


def test_flood_single_id():
    """
    Check that flooding works on single id
    """
    rule = FloodingRule(count=max_count)

    # Flood an id
    flood_id(rule=rule, id=0x1ac)


def test_flood_multiple_ids():
    """
    Check that flooding on one id does not affect another id that is not flooded
    """
    rule = FloodingRule(count=max_count)
    timestamp = 0.0

    # Flood an id
    flood_id(rule=rule, id=0x1ac)

    # Do another id up to max count and see if it returns anything
    # The whole point is to make sure one flooded id doesn't count another id as flooded
    for i in range(max_count): # Exceed max count by 1
        message = Message(id=0x234, payload=bytes([200]), timestamp=timestamp) # Use same id
        assert rule.check(message) is None
        timestamp += 0.1 # Increment timestamp
