# Model plan (Stage II)

None of these models is trained or deployed yet. This is the plan we will execute in Stage II and the
targets we will measure. Models will be compiled with the Hailo Dataflow Compiler and run through
HailoRT on the ASUS UGen300; where a suitable pre-trained model exists in the Hailo Model Zoo we start from it.

| Model | Runs on | Input | Output | Starting point | Stage II target |
|---|---|---|---|---|---|
| Thermal person detection | UGen300 | Thermal video frames | Person boxes + confidence | YOLO-family detector, fine-tuned on public thermal datasets | ≥ 90% recall within 5 m on a public test set |
| CCTV person detection + re-identification | UGen300 | Recorded pre-fire CCTV | Per-person tracks: last-seen position, heading, seen leaving | Person detector + re-ID embedding model | Track each person across cameras on recorded test clips |
| Dog-alert classifier | UGen300 | Harness audio + motion | "Alert" / "no alert" | Small audio + motion classifier | Measured on recorded dog-training sessions |
| Firefighter-down view check | UGen300 | Helmet camera frames | View frozen / pointing at floor or ceiling | Lightweight image model | Part of a ≤ 40 s down-to-alert target in drills |
| Radio keyword spotting | Host CPU | Radio audio | Keywords ("air", "mask", "Mayday"), Mandarin and Taiwanese | Small keyword-spotting model | ≥ 90% of keywords caught in recorded fireground noise |

## System targets

- At least 4 video streams at 10+ frames per second each on one UGen300.
- At most 1 second from a sensor frame to an updated map, fully offline.

## How the models connect to this repository

Each model's output becomes an event for the probability map:

| Model output | Map update |
|---|---|
| CCTV track (last-seen x, heading) | Starting probability for each room (`ProbabilityMap.__init__`) |
| Thermal search with no person found | `searched_and_empty(room)` |
| Thermal person found | `searched_and_found(room)` |
| Dog alert / no alert at a door | `dog_passed(room, alerted)` |

In Stage II we replace the simulated sensor draws with these real outputs and measure the real detection
rates, then re-run the benchmark with the measured values in `config.py`.

## Data and privacy

Public datasets and recorded drills only. No real building CCTV is used before a personal-data review
and an opt-in agreement with building management.
