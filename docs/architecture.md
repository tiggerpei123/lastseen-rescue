# Architecture

LastSeen has three layers. Nothing in the chain uses the internet or a cell tower.

## 1. Field sensors

| Sensor | What it sends | Notes |
|---|---|---|
| Helmet or handheld thermal camera | Person detections (unit · floor · zone · class · confidence · time), about 40 bytes each | Detection runs near the camera where possible; otherwise low-resolution thermal snapshots |
| Search-dog harness (microphone + motion sensor) | "Alert" events when the dog's bark-and-stop pattern is recognised | |
| Building CCTV recorder | The last minutes of recording before smoke, read over a cable in the lobby or control room | Pre-fire video only |
| Fireground radio | Audio tapped from the receiver already in the command vehicle | For keyword alerts ("air", "mask", "Mayday") |
| Position and vital-sign feeds | From existing systems (NFA positioning tags, Kaohsiung 5G system) where available | LastSeen does not build its own positioning |

## 2. Command-vehicle edge node

**ASUS UGen300 (Hailo-10H, 40 TOPS INT4, 8 GB)** runs the vision models:
thermal person detection, CCTV person detection and re-identification, the dog-alert classifier and the
firefighter-down view check.

**Host PC (CPU)** runs the lighter logic:

- **Probability map** — one probability per room that someone is still trapped there. It starts from CCTV
  last-seen tracks and is updated by every search result and dog pass (Bayesian odds updates).
  Implemented in [`lastseen_sim/probability_map.py`](../lastseen_sim/probability_map.py).
- **Route planner** — proposes the next room for each crew: highest probability per second of travel
  plus search. Implemented as the `lastseen` strategy in [`lastseen_sim/simulate.py`](../lastseen_sim/simulate.py).
- **Alert engine** — firefighter-down signals and radio keywords (Stage II).
- **Decision log** — every recommendation and every commander decision, for after-action review.

## 3. Outputs

- Commander tablet: the map, a headcount (seen / left / missing), and approve, edit or reject for every route.
- Approved routes go to helmet displays, as digital-radio text, or are read out by the commander.
- Urgent alerts go to the rapid intervention team.

## Links without internet

1. **Send results, not video** — tiny detection messages pass through walls on slower, longer-range radio.
2. **Drop-in relays** — battery relays placed in stairwells as crews advance (existing products, NCC-approved).
3. **Store and forward** — in a dead zone, data is kept with timestamps and sent when back in range.
   Too slow for emergencies, so down and radio alerts depend on the relay chain.

## What is in this repository today

| Component | Status |
|---|---|
| Probability map | Working, in simulation |
| Route planner | Working, in simulation and benchmarked |
| Vision models on UGen300 | Planned for Stage II ([model_plan.md](model_plan.md)) |
| Commander approval UI, alerts, relays | Planned for Stage II ([stage2_plan.md](stage2_plan.md)) |
