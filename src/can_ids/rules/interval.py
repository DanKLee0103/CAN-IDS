from typing import Dict, List, Optional, Set
from collections import defaultdict

from ..message import Message

class IntervalRule:
    name = "IntervalRule"

    def __init__(self, whitelist: List[int]):
        self.whitelist_set = set(whitelist)
        self.whitelist = {id: 0 for id in whitelist}
        self.timestamp_boundary = 0.001

    
