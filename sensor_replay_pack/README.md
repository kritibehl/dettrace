# DetTrace Sensor Replay Pack

This pack validates synthetic GPS/IMU-style trajectory events before downstream trajectory or map-generation workflows.

## Checks

- timestamp ordering
- dropped event detection
- duplicated event detection
- delay and jitter detection
- first-divergence isolation
- invalid trajectory-segment reporting

## Run

    python3 sensor_replay_pack/run_sensor_replay.py

## Safe scope

Synthetic sensor-stream replay and data-integrity validation only.

This does not claim real GPS/IMU ingestion, autonomous-driving systems, map creation, localization, sensor fusion, lidar, radar, camera perception, or production NVIDIA tooling.
