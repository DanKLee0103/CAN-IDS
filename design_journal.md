# Design Journal - CAN Intrusion Detection System

**Project Goal:** Build a real-time intrusion detection system for automotive CAN bus networks

**Timeline:** 10 weeks, 30 hours total (3 hrs/week) - most likely longer

---

## Week 0: Planning & Architecture Decisions

### Decision 1: Detection Approach

**Date:** [Today's date]

**Options Considered:**
1. Rule-based detection (frequency analysis, ID validation, range checks)
2. Machine learning-based detection (anomaly detection models)
3. Hybrid approach (rules + simple ML)

**My Choice:** Rule-based detection

**Rationale:**
- Only have 30 hours total for the project
- Rule-based is deterministic and explainable (important for automotive safety)
- ML would require training data preparation, model tuning, validation (10+ hours alone)
- Automotive systems need predictable behavior - rules provide that
- Can still achieve 90%+ detection accuracy with well-designed rules

**Trade-offs:**
- Giving up: Potentially higher detection accuracy from ML
- Gaining: Faster development, deterministic behavior, easier to debug, more explainable results

---

### Decision 2: Attack Types to Detect

### Attack Types - Full Analysis

**CAN Bus Attack Types I Researched:**

1. **Message Flooding (DoS)** - IMPLEMENTING ✅
   - Saturate bus bandwidth with high-frequency messages
   - Detection: Monitor message frequency per CAN ID
   
2. **ID Spoofing** - IMPLEMENTING ✅
   - Impersonate legitimate ECU by using its CAN ID
   - Detection: Whitelist validation + duplicate ID detection
   
3. **Payload Anomalies** - IMPLEMENTING ✅
   - Send messages with out-of-range or malicious data
   - Detection: Range validation on payload fields
   
4. **Timing Attacks** - NOT implementing
   - Disrupt periodic message timing
   - Would require: Timing analysis of periodic messages (~10 hrs implementation)
   - Less common in literature, harder to simulate
   
5. **Bus-Off Attacks** - NOT implementing
   - Force ECUs offline by triggering error states
   - Would require: Hardware-level error monitoring
   - Cannot simulate reliably in software-only environment

**My Choice:** Focus on flooding, spoofing, and payload anomalies (3 types)

**Why I chose flooding, spoofing, and payload:**
- Most well-documented in literature (used in Jeep hack, other real attacks)
- Can be simulated with software datasets
- Cover 80% of real-world attack scenarios
- Achievable detection implementation in 30-hour timeframe

**Trade-offs:**
- Not covering timing/bus-off attacks, but those are less common and harder to simulate

---

### Decision 3: Implementation Language

**My Choice:** Python

**Rationale:**
- `python-can` library handles CAN message parsing
- Fast prototyping (critical for 30-hour budget)
- Easy multi-threading with `threading` module
- pandas/numpy for performance analysis
- Can still achieve 10,000+ messages/sec throughput

**Trade-offs:**
- C/C++ would be "more embedded" but would take 2-3x longer to develop
- For this project, speed of development > absolute performance

---

## Week 1: [To be filled in during Week 1]

### What I Built:
...

### Challenges:
...

### How I Solved Them:
...

---