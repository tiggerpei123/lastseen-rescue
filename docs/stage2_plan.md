# Stage II plan (6 November – 4 December 2026)

Goal: run the real models on the UGen300 and show the whole loop — sensors → map → recommended route →
commander approval — with every network switched off.

| Week | Build | Done when |
|---|---|---|
| W1 | Thermal detector and CCTV re-ID compiled for the UGen300 | Frame rates measured for 1, 2 and 4 streams |
| W2 | Live map from two thermal cameras, motion sensors and recorded CCTV | Map updates on screen from real sensor input |
| W3 | Commander approval flow; firefighter-down and radio-keyword alerts | Approve / edit / reject works; alerts fire on test recordings |
| W4 | Full test with all networks off; KPI measurement; demo video | KPI table filled in with measured values |

## Hardware

The UGen300 provided by the organiser (USB or M.2), a host mini PC, two USB thermal cameras standing in
for helmet cameras, two small boards with motion sensors, and three Wi-Fi mesh nodes acting as relays.
Hardware other than the UGen300: about US$1,500 (estimate).

## Stage II KPIs

| KPI | Target |
|---|---|
| Thermal person-detection recall within 5 m (public test set) | ≥ 90% |
| Video streams on one UGen300 | ≥ 4 at 10+ fps each |
| Sensor frame to updated map, offline | ≤ 1 s |
| Radio keywords caught in recorded fireground noise | ≥ 90% |

## Deliverables

Updated repository with model files and compile scripts, measured KPI table, the benchmark re-run with
measured sensor rates, and a demo video showing the UGen300 running.
