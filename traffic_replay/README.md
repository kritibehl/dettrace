# Traffic Capture / Replay Example

This directory contains structured mock traffic replay examples for DetTrace.

## Scope

This is not packet capture, tcpdump, Wireshark integration, or production network tracing.

It demonstrates how HTTP/TCP/TLS-style events can be represented as replayable diagnostic traces.

## Example

`http_capture_replay_example.json` compares:

    expected: dns_resolve -> tcp_connect -> tls_handshake -> http_request -> http_200
    actual:   dns_resolve -> tcp_connect -> tls_handshake_timeout -> retry_connect -> http_unavailable

## Debugging value

The replay identifies the first divergence at the TLS handshake stage before the later HTTP unavailable symptom appears.
