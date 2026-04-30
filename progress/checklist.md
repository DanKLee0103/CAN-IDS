# CAN-IDS Progress Checklist

## Phase 1 — Core Implementation (Weeks 1-5)
- [x] `Message` class — CAN message data model with validation
- [x] `FloodingRule` — sliding window frequency detection
- [x] `Detector` — rule coordinator
- [x] `SpoofingRule` — whitelist + duplicate sender detection
- [x] `PayloadRule` — byte-range validation
- [x] `TrafficGenerator` — generate normal + attack traffic for testing
- [ ] `test_flooding.py`
- [ ] `test_spoofing.py`
- [ ] `test_payload.py`

## Phase 2 — Validation (Weeks 6-8)
- [ ] Find and load a real CAN attack dataset (e.g. OTIDS)
- [ ] Run IDS against dataset
- [ ] Measure detection rate and false positive rate
- [ ] Tune rule thresholds based on results

## Phase 3 — Polish (Weeks 9-10)
- [ ] Write README with results and numbers
- [ ] Clean up code, add type hints throughout
- [ ] Finalize design journal
