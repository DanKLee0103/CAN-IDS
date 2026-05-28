# Design Journal - CAN Intrusion Detection System

**Project Goal:** Build a real-time intrusion detection system for automotive CAN bus networks

**Timeline:** 10 weeks, 30 hours total (3 hrs/week) - most likely longer

---

## Week 0: Planning & Architecture Decisions

### Decision 1: Detection Approach

**Project Start Date:** 2/14/2026

**Options Considered:**
1. Rule-based detection (frequency analysis, ID validation, range checks)
2. Machine learning-based detection (anomaly detection models)
3. Hybrid approach (rules + simple ML)

**My Choice:** Rule-based detection

**Rationale:**
- Have about 30 hours total for the project
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

**My Choice:** Focus on flooding, spoofing, and payload anomalies (3 types) by using OTIDS dataset

**Why I chose flooding, spoofing, and payload:**
- Most well-documented in literature
- Can be simulated with software datasets
- Covers real-world attack scenarios
- Achievable detection implementation in 30-hour timeframe

**Trade-offs:**
- Not covering timing/bus-off attacks, but those are less common and harder to simulate

---

### Decision 3: Implementation Language

**My Choice:** Python

**Rationale:**
- Fast prototyping (critical for 30-hour budget)
- Can still achieve 10,000+ messages/sec throughput -> achieved ~21,661 messages/sec throughput (measured using time module)
- csv module used to parse dataset(s)
- ~~`python-can` library handles CAN message parsing~~
- ~~~Easy multi-threading with `threading` module~~
- ~~pandas/numpy for performance analysis~~

**Trade-offs:**
- C/C++ would be "more embedded" but would take 2-3x longer to develop
- For this project, speed of development > absolute performance

---

## Week 1: File Structure, Prototype Detector, Rules Setup

### What I Built:
- `Message` class — CAN message data model with ID validation (11-bit vs 29-bit), payload length check
- `FloodingRule` — sliding window frequency detection using a dict of timestamp lists per CAN ID
- `Detector` — coordinator that runs all rules on each incoming message and collects alerts
- Project file structure established
```
CAN-IDS/
├── pyproject.toml
├── src/
│   ├── evaluate.py
│   ├── can_ids/
│   │   ├── __init__.py
│   │   ├── message.py
│   │   ├── detector.py
│   │   ├── loader.py
│   │   ├── extract.py
│   │   └── rules/
│   │       ├── __init__.py
│   │       ├── flooding.py
│   │       ├── spoofing.py
│   │       └── payload.py
│   └── simulator/
│       ├── __init__.py
│       └── generator.py
├── tests/
│   ├── __init__.py
│   ├── test_flooding.py
│   ├── test_spoofing.py
│   └── test_payload.py
├── otids_dataset/
│   ├── attack_free.csv
│   ├── DoS_flood.csv
│   ├── Fuzzy_spoof_payload.csv
│   └── Impersonation_spoof.csv
└── progress/
    └── checklist.md
```

### Challenges:
- Uncertainty in structure due to:
   - Future testing
   - Clarity in different directories
- Ensuring flooding rule is accurate and functional

### How I Solved Them:
- Used AI for potential outlines and designs (did not end up using any of these)
- Pros and cons for each design
- Ultimately created a structured design with clear future steps
- Researched flooding rule and implemented sliding window for flooding detection on any id

---

## Week 2: Remaining Rules and Simulator

### What I Built:
- `SpoofingRule` — whitelist validation + duplicate sender detection using timestamp gap check
- `PayloadRule` — byte-range validation against a configurable spec dict per CAN ID
- `TrafficGenerator` — simulates normal traffic and three attack scenarios (flood, spoof, payload)

### Challenges:
- Designing `SpoofingRule` to handle both whitelist and duplicate sender detection without conflating the two mechanisms
- Deciding how to represent payload specs — needed to store byte position, byte length, and valid range per CAN ID
- Understanding that `payload` in CAN is vehicle-specific, so specs had to be placeholder values without a DBC file

### How I Solved Them:
- Separated whitelist tracking and timestamp tracking into two distinct data structures in `SpoofingRule`
- Used a nested dict structure: `CAN ID → (start_byte, end_byte, (min_val, max_val))`
- Used `int.from_bytes()` to extract multi-byte values from payload for range validation

---

## Week 3-4: Testing

### What I Built:
- `test_flooding.py`, `test_spoofing.py`, `test_payload.py` — unit tests for all three rules
- All tests passing with pytest

### Challenges:
- `FloodingRule` check returned stale count because local variable wasn't written back to the dict after filtering old timestamps
- `SpoofingRule` tests needed to avoid triggering the duplicate sender check on the first message (initial timestamp is 0, causing false alerts at small timestamps)
- `PayloadRule` byte extraction failed with `int()` on raw bytes — needed `int.from_bytes()`
- Test payloads had to be `bytes` type, not plain integers

### How I Solved Them:
- Fixed sliding window by writing the filtered slice back to `self.record[message.id]`
- Used `ts=1.0` as starting timestamp in spoofing tests to ensure gap from initial 0 is always large
- Switched to `int.from_bytes(payload[start:end], byteorder="big")` for byte extraction
- Used `bytes([value])` or `b"\x0b\xb8..."` notation for test payloads

---

## Week 5-7: Dataset Evaluation

### What I Built:
- `loader.py` — parses OTIDS dataset CSV files into Message objects
- `extract.py` — extracts whitelist IDs and max normal message frequency from attack-free dataset, and extracts anything else I need as well
- `evaluate.py` — runs detector against all datasets, measures detection rate and false positive rate

### Results:
- DoS detection rate: 100%
- Overall detection rate: 72.27%
- False positive rate: 4.70%
- Throughput: 35,627 msgs/sec (exceeds real CAN bus rate of 2,000–10,000 msgs/sec)

### Challenges:
- Figuring out the root cause of detection rate < 90%
- Payload detection not found useful among the OTIDS datasets due to lack of specs for each id

### How I Solved Them:
- No valid solution in given timeframe. ML approach would take much more time to implement.
- Future approach is to use a time skew detection approach, which measures the bias/noise in each ECU (id) timer (typically a crystal oscillator). If data is out of bias range, we flag it.
- If time skew detection invalid, ML approach would be tested.
---

## Week 8-10: Analysis and Documentation

### What I Found:
- DoS detection achieves 100% detection rate with 4.70% false positive rate — rule-based flooding detection is highly effective for high-frequency attacks
- Impersonation detection is fundamentally limited by the attack strategy: the attacker sends `0x164` at only 130 msgs/sec vs the legitimate ECU's 124 msgs/sec — too close to distinguish with frequency rules
- The OTIDS impersonation dataset labels the entire attack period (including legitimate ECU messages) as `target=3`, which inflates false negatives — the first 250 seconds must be excluded from evaluation
- Payload validation (`PayloadRule`) could not be meaningfully evaluated on OTIDS because the dataset does not include a DBC file specifying what each byte in each CAN ID represents
- Interval variance analysis was explored as an alternative impersonation detection approach but found infeasible — natural timing jitter for `0x164` in normal traffic (std dev = 3.3ms) overlaps with the attack pattern gap distribution

### Limitations:
- Rule-based detection cannot reliably detect impersonation attacks where the attacker mimics normal message rates — requires clock-skew analysis or ML
- `PayloadRule` requires vehicle-specific signal definitions (DBC file) not publicly available for the Kia Soul used in OTIDS
- `FloodingRule` threshold must be tuned per-vehicle — the 125 msgs/sec threshold was derived empirically from this dataset and may not generalize

### Future Work:
- **Clock-skew detection**: fingerprint each ECU's crystal oscillator drift over time — attackers using different hardware will have a different drift signature even at normal message rates
- **ML-based anomaly detection**: train a model on normal traffic patterns to flag subtle deviations that rules cannot capture
- **C/C++ port**: reimplement core detection logic in C for embedded deployment on actual vehicle hardware
- **DBC file integration**: source or reverse-engineer signal definitions to enable meaningful payload validation


## References

Hyunsung Lee, Seong Hoon Jeong, and Huy Kang Kim, "OTIDS: A Novel Intrusion Detection System for In-vehicle Network by using Remote Frame," PST (Privacy, Security and Trust), 2017.

---
