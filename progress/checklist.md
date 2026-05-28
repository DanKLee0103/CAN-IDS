# CAN-IDS Progress Checklist

## Phase 1 — Core Implementation (Weeks 1-5)
- [x] `Message` class — CAN message data model with validation
- [x] `FloodingRule` — sliding window frequency detection
- [x] `Detector` — rule coordinator
- [x] `SpoofingRule` — whitelist + duplicate sender detection
- [x] `PayloadRule` — byte-range validation
- [x] `TrafficGenerator` — generate normal + attack traffic for testing
- [x] `test_flooding.py`
- [x] `test_spoofing.py`
- [x] `test_payload.py`

## Phase 2 — Validation (Weeks 6-8)
- [x] Find and load a real CAN attack dataset (e.g. OTIDS)
- [x] Run IDS against dataset
- [x] Measure detection rate and false positive rate
- [x] Tune rule thresholds based on results

## Phase 3 — Polish (Weeks 9-10)
- [ ] Write README with results and numbers
- [ ] Clean up code, add type hints throughout
- [ ] Finalize design journal
