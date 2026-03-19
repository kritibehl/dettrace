#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace dettrace {

enum class DistributedEventType {
    REQUEST_START,
    CLIENT_SEND,
    SERVER_RECEIVE,
    SERVER_SEND,
    RESPONSE_RECEIVE,
    TIMEOUT,
    RETRY,
    CANCEL,
    NETWORK_ERROR,
    FAILOVER,
    RECOVERY,
    DEPLOY,
    HEALTH_CHANGE
};

std::string to_string(DistributedEventType t);

struct DistributedEvent {
    uint64_t seq = 0;
    uint64_t ts_ms = 0;
    DistributedEventType type = DistributedEventType::REQUEST_START;

    std::string request_id;
    std::string span_id;
    std::string parent_span_id;

    std::string service;
    std::string downstream_service;

    std::string status;
    std::string failure_reason;

    int retry_attempt = 0;
    int latency_ms = 0;
    bool cancelled = false;

    std::vector<std::string> annotations;
};

struct BlastRadiusSummary {
    std::string root_service;
    std::vector<std::string> directly_impacted_services;
    std::vector<std::string> upstream_services;
    int retry_events = 0;
    int timeout_events = 0;
    int network_error_events = 0;
};

struct TimelineCorrelationSummary {
    bool deploy_correlated = false;
    bool failover_observed = false;
    int max_latency_ms = 0;
    int error_burst_count = 0;
    int window_start_ms = 0;
    int window_end_ms = 0;
    std::string suspected_trigger;
};

std::vector<DistributedEvent> build_cascading_timeout_pack();
std::vector<DistributedEvent> build_retry_storm_pack();
std::vector<DistributedEvent> build_misordered_recovery_pack();
std::vector<DistributedEvent> build_failover_edge_pack();

void write_distributed_trace_jsonl(const std::string& path, const std::vector<DistributedEvent>& events);
std::vector<DistributedEvent> read_distributed_trace_jsonl(const std::string& path);

std::vector<DistributedEvent> annotate_network_events(const std::vector<DistributedEvent>& events);
std::vector<DistributedEvent> replay_distributed_incident(const std::vector<DistributedEvent>& expected);

std::vector<DistributedEvent> ingest_otel_jsonl_as_events(const std::string& path);
TimelineCorrelationSummary correlate_incident_timeline(const std::vector<DistributedEvent>& events,
                                                       uint64_t deploy_ts_ms,
                                                       int correlation_window_ms);
BlastRadiusSummary infer_blast_radius(const std::vector<DistributedEvent>& events);

std::string build_incident_report_json(const std::vector<DistributedEvent>& baseline,
                                       const std::vector<DistributedEvent>& candidate);
std::string build_semantic_diff_json(const std::vector<DistributedEvent>& baseline,
                                     const std::vector<DistributedEvent>& candidate);

}  // namespace dettrace
