# Sensor Stream Integrity Report

## Safe claim

synthetic GPS/IMU-style trajectory data validation; not production autonomy or map creation

## Summary

- expected event count: `6`
- observed event count: `6`
- first divergence index: `3`
- dropped events: `1`
- duplicated events: `1`
- delayed events: `1`
- out-of-order events: `1`
- trajectory valid for downstream mapping: `False`

## First divergence

- details: `{'index': 3, 'expected_event_id': 'imu_002', 'observed_event_id': 'gps_002', 'expected_timestamp_ms': 300, 'observed_timestamp_ms': 200}`

## Invalid trajectory segment

- start index: `3`
- end index: `5`

## Interpretation

The observed sensor stream contains integrity failures before downstream trajectory or map-generation use. The replay isolates the earliest divergence and reports dropped, duplicated, delayed, and out-of-order records.
