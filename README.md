# CAN-IDS — CAN Bus Intrusion Detection System

A rule-based intrusion detection system for automotive CAN bus networks, implemented in Python and evaluated against the OTIDS dataset (Kia Soul, 2017).

---

## Overview

Modern vehicles communicate internally via the CAN bus protocol. Because CAN has no built-in authentication, attackers with physical or remote access can inject malicious messages. This project implements a real-time IDS that detects three classes of attacks:

- **DoS (Flooding)** — high-frequency message injection that saturates bus bandwidth
- **Spoofing** — unknown CAN IDs or duplicate senders impersonating legitimate ECUs
- **Payload Anomalies** — out-of-range byte values in known message fields

---

## Architecture

```
src/
  can_ids/
    message.py      # CAN message data model (ID validation, payload)
    detector.py     # Coordinator — runs all rules on each message
    loader.py       # Parses OTIDS CSV dataset into Message objects
    extract.py      # Extracts whitelist IDs and frequency thresholds
    rules/
      flooding.py   # Sliding window frequency detection per CAN ID
      spoofing.py   # Whitelist validation + duplicate sender detection
      payload.py    # Byte-range validation against configurable spec
  simulator/
    generator.py    # Generates synthetic normal and attack traffic
evaluate.py         # Runs detector against dataset, reports metrics
tests/
  test_flooding.py
  test_spoofing.py
  test_payload.py
```

---

## Results

Evaluated on the OTIDS Car Hacking Dataset (Kia Soul):

| Metric | Value |
|---|---|
| DoS detection rate | 100% |
| Overall detection rate | 72.27% |
| False positive rate | 4.70% |
| Throughput | 35,627 msgs/sec |

Real CAN bus bandwidth: ~2,000–10,000 msgs/sec. The system processes messages at 3–17x real-time speed, confirming real-time detection capability.

---

## How to Run

**Install:**
```bash
pip install -e .
```

**Run tests:**
```bash
pytest
```

**Run evaluation against OTIDS dataset:**
```bash
cd src
python evaluate.py
```

---

## Limitations

- **Impersonation detection** is limited — the OTIDS attacker sends `0x164` at 130 msgs/sec vs the legitimate ECU's 124 msgs/sec, too close to distinguish with frequency-based rules. Requires clock-skew analysis or ML.
- **Payload validation** requires a vehicle DBC file (signal definitions) not publicly available for this dataset.
- Flooding threshold (125 msgs/sec) was tuned empirically for this dataset and may not generalize to other vehicles.

---

## Dataset

[OTIDS — Car Hacking Dataset](https://ocslab.hksecurity.net/Datasets/CAN-intrusion-dataset) by Hyun Min Song et al. (2017). Captured from a Kia Soul. Contains labeled DoS, fuzzy, and impersonation attacks.