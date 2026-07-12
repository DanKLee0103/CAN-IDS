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

### Future Work (at time of submission):
- **Clock-skew detection**: fingerprint each ECU's crystal oscillator drift over time — attackers using different hardware will have a different drift signature even at normal message rates *(implemented post-submission — see below)*
- **ML-based anomaly detection**: train a model on normal traffic patterns to flag subtle deviations that rules cannot capture
- **C/C++ port**: reimplement core detection logic in C for embedded deployment on actual vehicle hardware
- **DBC file integration**: source or reverse-engineer signal definitions to enable meaningful payload validation

---

## Post-Submission: Clock-Skew Detection & Web Dashboard

### Motivation

The final report identified impersonation detection as the fundamental gap in the system — the attacker sends on ID 0x164 at 130 msgs/sec vs the legitimate ECU's 124 msgs/sec, too close for frequency rules to distinguish. Clock-skew detection was listed as the highest-priority future improvement, so it was implemented first.

### Decision 4: Clock-Skew Detection Approach

**Core idea:** Every ECU's crystal oscillator drifts at a unique rate. Over time, the accumulated difference between actual timestamps and expected timestamps (based on mean interval) grows linearly. The slope of that drift line is a hardware fingerprint. An attacker using different hardware will have a different slope.

**Implementation:**

For each CAN ID, compute a baseline slope from attack-free traffic:
```
error[i] = actual_timestamp[i] - (first_timestamp + i * mean_interval)
slope = polyfit(range(n), errors, degree=1)[0]
```

During live detection, maintain a sliding window of the last 200 messages per ID. Compute the live slope over that window and compare against the baseline. If the difference exceeds the threshold (`error_range = 1e-4`), fire an alert.

**Key design decisions:**

- **Global indices, not local window indices**: When the deque slides (drops old messages), a local index starting at 0 each time would produce an unstable slope estimate. Instead, `msg_counts` tracks the cumulative message count per ID from the very first message ever seen. This keeps the slope estimate stable as the window moves.

- **`first_timestamps` never resets**: The error calculation uses `first_timestamp` as a fixed reference point. Resetting it when the window slides would corrupt the accumulated error baseline.

- **Minimum 30 messages before firing**: polyfit on fewer points produces unreliable slope estimates — early return below this count avoids false positives at startup.

- **No check interval**: Running polyfit every message (not every N messages) is required to maintain 84% detection. Testing with check_interval=50 or 500 dropped detection to ~72%.

- **Warmup with attack-free data**: ClockSkewRule needs `first_timestamps` and enough messages to fill the deque before it can meaningfully compare slopes. Processing 5k–20k attack-free messages before the target dataset raises impersonation detection from ~0% to 42%.

- **Only ClockSkewRule needs warmup**: FloodingRule and SpoofingRule are reset after warmup to prevent timestamp contamination — attack-free timestamps leaking into the flood window would cause false positives at the start of the target dataset.

**Trade-offs:**
- Threshold `1e-4` balances detection rate (84%) against false positive rate (5.57%); tightening it raises FPR, loosening it lowers detection
- polyfit on 200 messages per message is O(n) per message — acceptable at 50k+ msgs/sec

### Results After Clock-Skew Addition

| Attack Type | Before | After | Notes |
|---|---|---|---|
| DoS (Flooding) | 100% | 96.27% | Slight change from evaluation methodology |
| Fuzzy (Spoofing) | ~100% | ~100% | Unchanged |
| Impersonation | ~0% | ~42% | ClockSkew detects hardware drift; combined with flooding/spoofing side effects |
| **Overall** | **72.27%** | **84.12%** | |
| False Positive Rate | 4.70% | 5.57% | ClockSkew contributes some FP on attack-free |
| Throughput | 35,627 msgs/sec | 50,000+ msgs/sec | Generator loader eliminated upfront memory allocation |

**Throughput improvement:** The original loader accumulated all rows into a list before yielding — for the 2.3M row attack-free dataset this blocked for several seconds before detection started. Converting to a generator (`yield` per row) gave ~4x throughput improvement and eliminated startup blocking.

### Decision 5: Web Dashboard (implemented using Claude Code)

A Flask web dashboard with real-time streaming was added to make the system interactive and demonstrable.

**Architecture:**
- Flask serves `index.html` and a `/stream` endpoint
- `/stream` uses Server-Sent Events (SSE): `Response(generate(), mimetype='text/event-stream')` — yields JSON data chunks while the detection loop runs
- The frontend uses `EventSource` to receive chunks and update Chart.js line charts, stat cards, and an alert log in real time

**Why SSE over WebSockets:** The data flow is strictly one-directional (server → client). SSE is simpler to implement server-side, requires no handshake, and works natively in browsers without a library.

**Flask threading:** `threaded=True, use_reloader=False` is required — without `threaded=True`, the long-running SSE generator blocks all other requests (page refresh hangs); without `use_reloader=False`, Flask's reloader spawns a second process that conflicts with the baseline preloading at startup.

**Baseline preloading:** `mean_intervals` and `baseline_slopes` are computed once at Flask startup (module level), not per request. Loading 2.3M rows of attack-free data takes ~15 seconds — doing it per request would make every run unusable.

**Batched SSE yields:** Different alerts fire on nearly every message — millions of individual SSE flushes caused the browser to freeze. Solution: collect alerts in `pending_alerts`, flush the last 10 every 2000 messages.

**Dashboard features:**
- Dataset selector (Attack Free, DoS Flood, Fuzzy/Spoof, Impersonation)
- Warmup size selector (Fast 5k / Standard 20k / Extended 100k / Extended 1m / Full) with caption explaining the tradeoff
- Flood threshold slider (50–300 msgs/sec) and ClockSkew sensitivity slider (1e-3 to 1e-5, log scale)
- Real-time Detection Rate and FPR line charts (Chart.js)
- Alert log with per-rule-type filter badges showing unique flagged IDs per rule

### Multi-Rule Detection Behavior

Each dataset is labeled by its primary attack type, but in practice every attack triggers multiple rules simultaneously — and this is expected, correct behavior.

During DoS flood, the attacker saturates the bus with a single ID at ~335k msgs/sec. This causes FloodingRule to fire on that ID, SpoofingRule to fire when consecutive messages from the same ID land within 1ms of each other, and ClockSkewRule to fire on all 45 ECUs because bus congestion delays every ECU's periodic messages, disrupting their timing fingerprints.

During impersonation, the attacker sends on a legitimate ID at a slightly elevated rate. The combined rate of real ECU + attacker exceeds the flood threshold, so FloodingRule fires. When the real ECU and the attacker happen to send within 1ms of each other, SpoofingRule fires. ClockSkewRule fires on the impersonated ID once enough messages accumulate to reveal the different hardware drift.

This redundancy is intentional — an attack that defeats one rule is likely still caught by another. The datasets are named for their *primary* attack vector, not for which rules will or won't fire on them.

### Parameter Tuning

**Warmup size:**
Controls how many attack-free messages are fed to ClockSkewRule before processing the target dataset. More warmup messages mean the sliding deque fills with stable baseline data, producing a more accurate slope estimate before any attack traffic arrives. 5k–20k messages is sufficient to fill the deque for all 45 ECU IDs (200 messages × 45 IDs = 9,000 minimum). Extended warmup (100k+) gives diminishing returns but costs startup time. Only ClockSkewRule benefits — FloodingRule and SpoofingRule are reset after warmup so their state is not contaminated by attack-free timestamps.

**Flood threshold (50–300 msgs/sec, default 125):**
The maximum number of messages any single CAN ID can send per second before FloodingRule fires. The default of 125 was derived from the maximum observed rate in the attack-free dataset (124 msgs/sec), ensuring no legitimate ECU ever triggers it. Raising the threshold reduces false positives but risks missing slower flood attacks that stay just above normal rates. Lowering it catches slower floods but increases false positives on high-frequency legitimate ECUs.

**ClockSkew sensitivity (1e-3 to 1e-5, default 1e-4):**
The maximum allowed difference between the live slope and the baseline slope before an alert fires. This is a log-scale parameter — small changes have a large effect. At 1e-4 (default): 84.12% detection, 5.57% FPR. Tightening to 1e-5 catches more subtle drift (potentially higher impersonation detection) but significantly raises FPR since natural timing jitter in normal traffic can approach this range. Loosening to 1e-3 reduces false positives to near zero but only catches attackers with very different hardware clocks. The 1e-4 default was chosen empirically as the best tradeoff on the OTIDS dataset.

### Updated File Structure

```
CAN-IDS/
├── src/
│   ├── app.py                  ← Flask web app with SSE streaming
│   ├── evaluate.py
│   ├── templates/
│   │   └── index.html          ← Dashboard UI
│   ├── can_ids/
│   │   ├── detector.py
│   │   ├── extract.py          ← get_mean_intervals(), get_baseline_slopes()
│   │   ├── loader.py           ← generator-based CSV parser
│   │   ├── message.py
│   │   └── rules/
│   │       ├── clockskew.py    ← new
│   │       ├── flooding.py
│   │       ├── payload.py
│   │       └── spoofing.py
└── tests/
    ├── test_clockskew.py       ← new
    ├── test_flooding.py
    ├── test_spoofing.py
    └── test_payload.py
```

## References

Hyunsung Lee, Seong Hoon Jeong, and Huy Kang Kim, "OTIDS: A Novel Intrusion Detection System for In-vehicle Network by using Remote Frame," PST (Privacy, Security and Trust), 2017.

---
