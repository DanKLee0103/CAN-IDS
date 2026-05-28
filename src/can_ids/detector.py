from typing import List

from .message import Message
from .rules.flooding import FloodingRule
from .rules.spoofing import SpoofingRule
from .rules.payload import PayloadRule

# Hold a list of all rules
# For each incoming message, call rule.check(msg) on each one
# Collect any non-None return values as alerts

class Detector:
    
    def __init__(self, count=20, whitelist=None): # arbitrary count as default
        self.rules = [FloodingRule(count), SpoofingRule(whitelist), PayloadRule()]
        self.alerts = []

    def process(self, message) -> List[str]:
        new_alerts = []
        for rule in self.rules:
            result = rule.check(message)
            if result is not None:
                self.alerts.append(result)
                new_alerts.append(result)
        return new_alerts

    def reset(self):
        for rule in self.rules:
            rule.reset()
        self.alerts = []
