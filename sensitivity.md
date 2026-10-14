# Sensitivity analysis (500 simulated fires per setting)

LastSeen vs current practice (nearest room first). One assumption changed at a time; the default value is in bold.

| Assumption | Value | First victim | Each victim |
|---|---:|---:|---:|
| Share of occupants seen on CCTV | 0.0 | 26% faster | 20% faster |
| Share of occupants seen on CCTV | 0.3 | 38% faster | 28% faster |
| Share of occupants seen on CCTV | **0.6** | 46% faster | 33% faster |
| Share of occupants seen on CCTV | 0.9 | 47% faster | 38% faster |
| Walking direction read correctly | 0.5 | 38% faster | 29% faster |
| Walking direction read correctly | **0.85** | 46% faster | 33% faster |
| Walking direction read correctly | 1.0 | 48% faster | 35% faster |
| Spread of the last-seen guess (m) | 1.5 | 44% faster | 32% faster |
| Spread of the last-seen guess (m) | **3.0** | 46% faster | 33% faster |
| Spread of the last-seen guess (m) | 6.0 | 45% faster | 32% faster |
| Thermal search finds a person in the room | 0.7 | 50% faster | 36% faster |
| Thermal search finds a person in the room | **0.85** | 46% faster | 33% faster |
| Thermal search finds a person in the room | 0.95 | 44% faster | 33% faster |
| Dog alerts at an occupied room | 0.3 | 39% faster | 20% faster |
| Dog alerts at an occupied room | **0.6** | 46% faster | 33% faster |
| Dog alerts at an occupied room | 0.9 | 50% faster | 41% faster |
| Seconds to search one room | 20.0 | 40% faster | 30% faster |
| Seconds to search one room | **40.0** | 46% faster | 33% faster |
| Seconds to search one room | 60.0 | 48% faster | 32% faster |
| Rooms per side of the corridor | 4 | 26% faster | 17% faster |
| Rooms per side of the corridor | **8** | 46% faster | 33% faster |
| Rooms per side of the corridor | 12 | 55% faster | 37% faster |
